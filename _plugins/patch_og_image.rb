# This monkey-patches the jekyll-og-image plugin to:
# 1. Prevent a NoMethodError merge! for String crash.
# 2. Force unique filenames for blog posts by using the Title instead of the Slug.
# 3. Redirect the config source to 'jekyll_og_image' to avoid conflict with 'og_image' string.
# 4. Fix a bug in the plugin where nested 'position' keys are not symbolized, causing a TypeError.

Jekyll::Hooks.register :site, :after_init do |site|
  if defined?(JekyllOgImage::Configuration)
    # Redirect config to jekyll_og_image key instead of og_image
    JekyllOgImage.config = JekyllOgImage::Configuration.new(site.config["jekyll_og_image"] || {})

    module JekyllOgImage
      class Configuration
        def merge!(other)
          safe_other = other.respond_to?(:to_h) ? other.to_h : {}
          safe_other = {} unless safe_other.is_a?(Hash)
          
          config = Jekyll::Utils.deep_merge_hashes(
            @raw_config.is_a?(Hash) ? @raw_config : {},
            safe_other
          )

          self.class.new(config)
        end

        # PATCH: Deeply symbolize position keys to prevent nil/TypeError crash
        def image
          img_config = if @raw_config["image"].is_a?(String)
            { "path" => @raw_config["image"] }
          elsif @raw_config["image"]
            @raw_config["image"].dup
          else
            {}
          end

          if img_config["position"]
            # Ensure it's a hash and symbolize keys
            pos = img_config["position"]
            if pos.is_a?(Hash)
              img_config["position"] = {
                x: (pos["x"] || pos[:x] || 0),
                y: (pos["y"] || pos[:y] || 0)
              }
            end
          end

          Image.new(**Jekyll::Utils.symbolize_hash_keys(img_config))
        end
      end

      class Generator < Jekyll::Generator
        private

        def process_collection(site, type, config)
          Jekyll.logger.info "Jekyll Og Image:", "Processing type: #{type} (Patched)" if config.verbose?

          items = get_items_for_collection(site, type)
          return if items.empty?

          base_output_dir = File.join(config.output_dir, type)
          absolute_output_dir = File.join(site.config["source"], base_output_dir)
          FileUtils.mkdir_p absolute_output_dir

          items.each do |item|
            if item.respond_to?(:draft?) && item.draft? && config.skip_drafts?
              next
            end

            fallback_basename = if item.respond_to?(:basename_without_ext)
                                  item.basename_without_ext
                                else
                                  File.basename(item.name, File.extname(item.name))
            end

            # PATCH: Prioritize title for slug generation to ensure uniqueness when titles contain dates
            slug = Jekyll::Utils.slugify(item.data["title"] || item.data["slug"] || fallback_basename)
            
            image_filename = "#{slug}.png"
            absolute_image_path = File.join(absolute_output_dir, image_filename)
            relative_image_path = File.join("/", base_output_dir, image_filename)

            if !File.exist?(absolute_image_path) || config.force?
              generate_image_for_document(site, item, absolute_image_path, config)
            end

            register_static_file(site, base_output_dir, image_filename, config) if File.exist?(absolute_image_path)

            item.data["image"] ||= {
              "path" => relative_image_path,
              "width" => JekyllOgImage.config.canvas.width,
              "height" => JekyllOgImage.config.canvas.height,
              "alt" => item.data["title"]
            }
          end
        end
      end
    end
  end
end
