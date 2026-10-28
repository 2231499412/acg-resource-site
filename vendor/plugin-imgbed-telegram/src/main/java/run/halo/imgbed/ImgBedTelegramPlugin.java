package run.halo.imgbed;

import org.springframework.stereotype.Component;
import run.halo.app.plugin.BasePlugin;
import run.halo.app.plugin.PluginContext;

@Component
public class ImgBedTelegramPlugin extends BasePlugin {
    public ImgBedTelegramPlugin(PluginContext pluginContext) { super(pluginContext); }
}
