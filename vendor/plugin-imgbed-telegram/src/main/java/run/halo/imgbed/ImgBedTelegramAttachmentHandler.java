package run.halo.imgbed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;
import lombok.extern.slf4j.Slf4j;
import org.pf4j.Extension;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.MediaTypeFactory;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.util.UriUtils;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;
import run.halo.app.core.attachment.ThumbnailSize;
import run.halo.app.core.extension.attachment.Attachment;
import run.halo.app.core.extension.attachment.Attachment.AttachmentSpec;
import run.halo.app.core.extension.attachment.Attachment.AttachmentStatus;
import run.halo.app.core.extension.attachment.Constant;
import run.halo.app.core.extension.attachment.Policy;
import run.halo.app.core.extension.attachment.endpoint.AttachmentHandler;
import run.halo.app.extension.ConfigMap;
import run.halo.app.extension.Metadata;

@Slf4j
@Extension
public class ImgBedTelegramAttachmentHandler implements AttachmentHandler {
    public static final String TEMPLATE_NAME = "imgbed-telegram";
    public static final String REMOTE_PATH_ANNO = "imgbed.halo.run/remote-path";
    private static final long DEFAULT_MAX_BYTES = 20L * 1024 * 1024;
    private final WebClient webClient = WebClient.builder().build();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public Mono<Attachment> upload(UploadContext context) {
        if (!shouldHandle(context.policy())) {
            return Mono.empty();
        }
        var properties = ImgBedTelegramProperties.from(context.configMap());
        if (!org.springframework.util.StringUtils.hasText(properties.getToken())
            && !org.springframework.util.StringUtils.hasText(properties.getAuthCode())) {
            return Mono.error(new IllegalStateException("ImgBed API token or upload auth code is not configured"));
        }
        long maxBytes = Math.max(1, properties.getMaxFileSizeMb()) * 1024L * 1024L;
        var file = context.file();
        var counter = new AtomicLong();
        Flux<DataBuffer> content = file.content().doOnNext(buffer -> {
            if (counter.addAndGet(buffer.readableByteCount()) > maxBytes) {
                throw new IllegalArgumentException("File exceeds ImgBed Telegram size limit (" + properties.getMaxFileSizeMb() + " MB)");
            }
        });
        var body = new MultipartBodyBuilder();
        body.asyncPart("file", content, DataBuffer.class)
            .filename(file.filename())
            .contentType(MediaType.APPLICATION_OCTET_STREAM);
        var uri = URI.create(properties.getEndpoint() + "/upload?uploadChannel=telegram&returnFormat=full"
            + (org.springframework.util.StringUtils.hasText(properties.getAuthCode())
            ? "&authCode=" + UriUtils.encodeQueryParam(properties.getAuthCode(), StandardCharsets.UTF_8) : "")
            + (org.springframework.util.StringUtils.hasText(properties.getLocation())
            ? "&uploadFolder=" + UriUtils.encodeQueryParam(properties.getLocation(), StandardCharsets.UTF_8) : ""));
        return webClient.post()
            .uri(uri)
            .headers(headers -> {
                if (org.springframework.util.StringUtils.hasText(properties.getToken())) {
                    headers.setBearerAuth(properties.getToken());
                }
            })
            .contentType(MediaType.MULTIPART_FORM_DATA)
            .body(BodyInserters.fromMultipartData(body.build()))
            .retrieve()
            .bodyToMono(String.class)
            .timeout(Duration.ofMinutes(5))
            .subscribeOn(Schedulers.boundedElastic())
            .flatMap(response -> buildAttachment(response, file.filename(), counter.get(), properties));
    }

    private Mono<Attachment> buildAttachment(String responseBody, String filename, long size,
                                               ImgBedTelegramProperties properties) {
        JsonNode response;
        try {
            response = objectMapper.readTree(responseBody);
        } catch (Exception e) {
            return Mono.error(new IllegalStateException("ImgBed returned invalid JSON: " + responseBody, e));
        }
        JsonNode item = response != null && response.isArray() && response.size() > 0
            ? response.get(0) : response;
        String url = text(item, "publicUrl");
        String src = text(item, "src");
        if (!org.springframework.util.StringUtils.hasText(url)) {
            url = src;
            if (url != null && url.startsWith("/")) {
                url = properties.getEndpoint() + url;
            }
        }
        if (!org.springframework.util.StringUtils.hasText(url)) {
            return Mono.error(new IllegalStateException("ImgBed 婵炴垶鎸搁敃锝囨閸洖绠ｉ柟閭﹀墮椤姴霉閿濆懏顥滈柟濂告敱閹棃寮幑鎰箑濠电偛澶囬崜婵嗭耿?src/publicUrl"));
        }
        String remotePath = remotePath(src, url);
        var metadata = new Metadata();
        metadata.setName(UUID.randomUUID().toString());
        var annotations = new HashMap<String, String>();
        annotations.put(Constant.EXTERNAL_LINK_ANNO_KEY, url);
        if (remotePath != null) {
            annotations.put(REMOTE_PATH_ANNO, remotePath);
        }
        metadata.setAnnotations(annotations);
        var spec = new AttachmentSpec();
        spec.setDisplayName(filename);
        spec.setSize(size);
        spec.setMediaType(MediaTypeFactory.getMediaType(filename).orElse(MediaType.APPLICATION_OCTET_STREAM).toString());
        var attachment = new Attachment();
        attachment.setMetadata(metadata);
        attachment.setSpec(spec);
        var status = new AttachmentStatus();
        status.setPermalink(url);
        attachment.setStatus(status);
        return Mono.just(attachment);
    }

    private static String text(JsonNode node, String field) {
        if (node == null || node.get(field) == null || node.get(field).isNull()) return null;
        return node.get(field).asText();
    }

    private static String remotePath(String src, String url) {
        String value = org.springframework.util.StringUtils.hasText(src) ? src : url;
        if (value == null) return null;
        try {
            String path = value.startsWith("http") ? URI.create(value).getPath() : value;
            if (path.startsWith("/file/")) path = path.substring("/file/".length());
            else if (path.startsWith("/")) path = path.substring(1);
            return path;
        } catch (Exception ignored) {
            return null;
        }
    }

    @Override
    public Mono<Attachment> delete(DeleteContext context) {
        if (!shouldHandle(context.policy())) return Mono.empty();
        var props = ImgBedTelegramProperties.from(context.configMap());
        if (!org.springframework.util.StringUtils.hasText(props.getToken())
            && !org.springframework.util.StringUtils.hasText(props.getAuthCode())) {
            return Mono.just(context.attachment());
        }
        String path = context.attachment().getMetadata().getAnnotations() == null ? null
            : context.attachment().getMetadata().getAnnotations().get(REMOTE_PATH_ANNO);
        if (!org.springframework.util.StringUtils.hasText(path)) return Mono.just(context.attachment());
        URI uri = URI.create(props.getEndpoint() + "/api/manage/delete/" + UriUtils.encodePath(path, StandardCharsets.UTF_8)
            + (org.springframework.util.StringUtils.hasText(props.getAuthCode())
            ? "?authCode=" + UriUtils.encodeQueryParam(props.getAuthCode(), StandardCharsets.UTF_8) : ""));
        return webClient.get().uri(uri)
            .headers(headers -> {
                if (org.springframework.util.StringUtils.hasText(props.getToken())) {
                    headers.setBearerAuth(props.getToken());
                }
            })
            .retrieve().toBodilessEntity()
            .timeout(Duration.ofMinutes(2))
            .thenReturn(context.attachment())
            .subscribeOn(Schedulers.boundedElastic());
    }

    @Override
    public Mono<URI> getPermalink(Attachment attachment, Policy policy, ConfigMap configMap) {
        if (!shouldHandle(policy)) return Mono.empty();
        var annotations = attachment.getMetadata().getAnnotations();
        if (annotations == null) return Mono.empty();
        String url = annotations.get(Constant.EXTERNAL_LINK_ANNO_KEY);
        return org.springframework.util.StringUtils.hasText(url) ? Mono.just(URI.create(url)) : Mono.empty();
    }

    @Override
    public Mono<URI> getSharedURL(Attachment attachment, Policy policy, ConfigMap configMap, Duration ttl) {
        return getPermalink(attachment, policy, configMap);
    }

    @Override
    public Mono<Map<ThumbnailSize, URI>> getThumbnailLinks(Attachment attachment, Policy policy, ConfigMap configMap) {
        return shouldHandle(policy) ? Mono.just(Map.of()) : Mono.empty();
    }

    boolean shouldHandle(Policy policy) {
        return policy != null && policy.getSpec() != null && TEMPLATE_NAME.equals(policy.getSpec().getTemplateName());
    }
}
