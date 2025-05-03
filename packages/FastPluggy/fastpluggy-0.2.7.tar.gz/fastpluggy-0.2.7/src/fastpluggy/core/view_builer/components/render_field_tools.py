from enum import Enum


class RenderFieldTools:

    @staticmethod
    def render_labels_field(labels):
        """
        Generate HTML for labels
        labels should be : [{"color": "blue","name": "Label Name"}]

        """
        if labels:
            label_html = ''
            for label in labels:
                name = label.get('name', '')
                color = label.get('color', '#000000')
                label_html += f'<span class="badge" style="background-color: {color};">{name}</span> '
            return label_html  # Markup to mark the string as safe HTML
        else:
            return '<span class="text-muted">No labels</span>'

    @staticmethod
    def render_enum(value):
        if isinstance(value, Enum):
            label = value.name.title()
            badge_class = value.badge_class if value.badge_class else 'badge-success'
            return f'<span class="badge {badge_class}">{label}</span>'
        return value

    @staticmethod
    def render_boolean(value):
        return '<span class="badge bg-green">Yes</span>' if value else '<span class="badge bg-red">No</span>'

    @staticmethod
    def render_icon(value):
        return f'<i class="{value}"></i>'

    @staticmethod
    def render_json_pre(content: str):
        import json
        try:
            obj = json.loads(content) if content else {}
            return f'<pre><code>{json.dumps(obj, indent=4)}</code></pre>'
        except Exception:
            return f'<code>{content}</code>'

    def render_bytes_size(size_bytes):
        if size_bytes == 0:
            return "0B"

        size_units = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0

        while size_bytes >= 1024 and i < len(size_units) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.2f} {size_units[i]}"
