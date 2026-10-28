package run.halo.imgbed;

import lombok.Data;
import org.springframework.util.StringUtils;
import run.halo.app.extension.ConfigMap;
import run.halo.app.infra.utils.JsonUtils;

@Data
public class ImgBedTelegramProperties {
    private String endpoint = "https://904764f8.cloudflare-imgbed-6ip.pages.dev";
    private String token;
    private String authCode;
    private String location = "halo";
    private Integer maxFileSizeMb = 20;

    public static ImgBedTelegramProperties from(ConfigMap configMap) {
        var props = new ImgBedTelegramProperties();
        if (configMap == null || configMap.getData() == null) {
            return props;
        }
        var json = configMap.getData().getOrDefault("default", "{}");
        if (StringUtils.hasText(json)) {
            var configured = JsonUtils.jsonToObject(json, ImgBedTelegramProperties.class);
            if (configured != null) {
                props = configured;
            }
        }
        if (!StringUtils.hasText(props.getEndpoint())) {
            props.setEndpoint("https://904764f8.cloudflare-imgbed-6ip.pages.dev");
        }
        props.setEndpoint(props.getEndpoint().replaceAll("/+$", ""));
        if (props.getMaxFileSizeMb() == null || props.getMaxFileSizeMb() < 1) {
            props.setMaxFileSizeMb(20);
        }
        return props;
    }
}
