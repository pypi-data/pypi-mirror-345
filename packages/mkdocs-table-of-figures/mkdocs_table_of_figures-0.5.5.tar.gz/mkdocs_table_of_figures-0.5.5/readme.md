# mkdocs-table-of-figures

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/mkdocs-table-of-figures)](https://pypi.org/project/mkdocs-table-of-figures/)

A MkDocs plugin that automatically generates figures with a figcaption, and lists all figures across your documentation into a *Table of Figures* that can be inserted into your Markdown pages.

## Summary

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Theme Recommendation](#theme-recommendation)
  - [Markdown Extensions](#markdown-extensions)
- [Figure Types](#figure-types)
  - [Built-in Types](#built-in-types)
  - [Priority Order](#priority-order)
- [Usage](#usage)
  - [Figure Detection](#figure-detection)
  - [Table Creation](#table-creation)
- [Customization](#customization)
  - [Custom Figure Types](#custom-figure-types)
  - [Translations](#translations)
  - [Custom Template](#custom-template)
- [Support](#support)
  - [Custom Attributes](#custom-attributes)
- [License](#license)
- [Roadmap](#roadmap)
- [Examples](#examples)
- [See Also](#see-also)

---

## Features

- **Automatic Figure Detection:**  
  Detects images, tables, code blocks, and custom figures in your Markdown files.

- **Table of Figures Generation:**  
  Builds a centralized list of all figures across your documentation, inserted wherever you place the directive.

- **Customizable Figure Types:**  
  Easily add your own figure patterns and templates using *regex* and *Jinja2*.

- **Custom Templates:**  
  Fully override the default output table layout using *Jinja2*.

- **Multilingual Support:**  
  Built-in translations for English (`en`), French (`fr`), and German (`de`), with easy customization.

---

## Installation

Install via pip:

```bash
pip install mkdocs-table-of-figures
```

---

## Configuration

Activate the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - table-of-figures:
      # directive_identifier: 'table-of-figures'
      # figure_types:
      #   - image
      #   - table
      #   - codeblock
        
      # custom_templates_path: null
      # translations_overrides_path: null

      # caption_identifier_description_separator: ' — '
      # sections_breadcrumb_separator: ' > '
```

---

### Theme Recommendation

It is highly recommended to use the [**Material for MkDocs**](https://squidfunk.github.io/mkdocs-material/) theme:

- If using another theme, you may need to **add custom CSS** for proper figure rendering and layout.
- Some figure types may **require additional CSS adjustments** outside of Material.

```yaml
theme:
  name: material
```

---

### Markdown Extensions

- `md_in_html` **must be enabled** if you are using the built-in figure types.
- `tables` **must be enabled** if you are using the default table template. (It's enabled by default when using the Material theme.)
- Additional extensions might be necessary depending on the figure types you use.

```yaml
markdown_extensions:
  - md_in_html
  - tables  # Enabled by default with the Material theme
```

---

## Figure Types

### Built-in Types

The plugin provides built-in figure types that can be referenced by name instead of defining a full configuration:

| Name        | Markdown Element                                    | Enabled by Default |
| ----------- | --------------------------------------------------- | ------------------ |
| `image`     | Markdown image                                      | ✅                 |
| `table`     | Markdown table                                      | ✅                 |
| `codeblock` | Markdown code block                                 | ✅                 |
| `mermaid`   | Code block with language set to `mermaid`           | ❌                 |
| `pair`      | Two markdown images separated and wrapped with `\|` | ❌                 |

---

### Priority Order

The **order of `figure_types`** in your config matters:

- Types listed earlier have **higher matching priority**.
- If multiple types could match the same element, **only the first match is applied**.

```yaml
plugins:
  - table-of-figures:
      figure_types:
        - pair     # Highest priority
        - image
        - table
        - mermaid
        - codeblock # Lowest priority
```

---

## Usage

Run `mkdocs build` or `mkdocs serve` to trigger the plugin if it is correctly configured.

You can **disable** the plugin temporarily with:

```yaml
plugins:
  - table-of-figures:
      enabled: false
```

Or **enable** it under specific conditions using *ENV variables*:

```yaml
plugins:
  - table-of-figures:
      enabled: !ENV [TOF, false]
```

```bash
TOF=true mkdocs build
```

---

### Figure Detection

The plugin scans for Markdown elements that have captions.  
If no caption is provided, the figure will be **ignored**.

- Captions can be empty but must still include opening and closing quotation marks (`" "`).

---

### Table Creation

Insert the table of figures anywhere (even multiple times) by using a directive:

```markdown
# Title

Page content...

<!-- <directive> -->

## Subtitle

More content...
```

- `<directive>` is defined by the `directive_identifier` option (defaults to `table-of-figures`).

---

## Customization

### Custom Figure Types

You can define custom figure types by providing full information inside `figure_types`:

| Key        | Type                    | Required | Description                                                                                   |
| ---------- | ----------------------- | -------- | --------------------------------------------------------------------------------------------- |
| `name`     | `str`                   | ✅       | The name of the figure type.                                                                  |
| `pattern`  | `str` (regex)           | ✅       | Regex pattern to match figures inside Markdown content.                                       |
| `template` | `str` (Jinja2 template) | ❌       | Jinja2 pattern to replace regex matches with rendered output.                                 |
| `metadata` | `dict`                  | ❌       | Arbitrary additional metadata, available inside the template. (Built-in types use an `icon`.) |

Example:

```yaml
plugins:
  - table-of-figures:
      figure_types:
        - image
        - table
        - name: custom
          pattern: '\{> (?P<custom>.+?) <\}\r?\n"(?P<caption>.*?)"'
          template: |
            <figure>
              {{ figure.match_groups.custom }}
              <figcaption>{{ figure.caption }}</figcaption>
            </figure>
          metadata:
            i: 1
            b: true
            s: 'one'
```

---

### Translations

Currently available languages:

- `en` (English)
- `fr` (French)
- `de` (German)

🤝 Feel free to open an [issue](https://gitlab.com/thiti-mkdocs-plugins/mkdocs-table-of-figures/-/issues) if you would like to submit a new language translation by providing a `translations.json` file!

You can **override translations** by specifying your own JSON file using `translations_overrides_path`.  
(The path is relative to the location of `mkdocs.yml`.)

Example structure:

```json
{
  "table": {
    "header": {
      "figure": "Figure",
      "category": "Category",
      "caption": "Caption"
    },
    "no_figures": "No figures to list..."
  },
  "caption": {
    "index": {
      "prefix": "Fig. ",
      "suffix": ""
    }
  },
  "figure_types": {
    "image": "Image",
    "table": "Table",
    "codeblock": "Code Block",
    "mermaid": "Diagram",
    "pair": "Image Pair"
  }
}
```

- You don't need to override everything, only the changed keys will apply.
- Fallback order: `en` → `theme language/locale` → `override file`.

---

### Custom Template

You can provide a **custom template** by creating a directory with an `output.md.j2` file and referencing it in `custom_templates_path`.

⚠️ Note: The template file in the directory **must** be named `output.md.j2`.

Here's the default template:

```jinja2
{%- if figures.size > 0 -%}

| {{ translations['table.header.figure'] or 'figure' }} | {{ translations['table.header.category'] or 'category' }} | {{ translations['table.header.caption'] or 'caption' }} |
| --- | --- | --- |

{%- for figure in figures %}
| [{{ figure.caption_identifier }}]({{ figure.uri }}) | {{ ':' ~ figure.figure_type_metadata.icon ~ ': ' if 'attr_list' in config.markdown_extensions and 'pymdownx.emoji' in config.markdown_extensions and figure.figure_type_metadata.get('icon') is not none }}{{ figure.figure_type_label }} | {{ figure.caption_description }} |
{%- endfor %}

{%- else %}
*`{{ translations['table.no_figures'] }}`*
{%- endif %}
```

---

## Support

### Custom Attributes

If the Markdown extension `attr_list` is enabled, you can use custom attributes for these built-in types:

- `image`
- `pair`

⚠️ Note: In the Material theme, `align=left` and `align=right` will be overridden by Material's figure styles.

---

## License

This project is licensed under the MIT License.  
See the [`license`](license) file for details.

---

## Roadmap

*Target goals for version 0.6.0.*

- [ ] Add Directive Options
  - [ ] Add option to include/exclude figures from specific files in the table
  - [ ] Add option to include/exclude figures of specific types in the table
- [ ] Add Unit Testing
  - [ ] Add unit tests for figure detection
  - [ ] Add unit tests for table generation
  - [ ] Automate tests in GitLab CI pipeline
  - [ ] Add coverage reporting and badge

---

## Examples

You can find ready-to-use examples in the [`examples`](examples/) directory.

- [`minimal`](examples/minimal): Shows how to set up a minimal usage of the plugin.
- [`simple`](examples/simple): Shows how to set up a full usage with built-in figure types.
- [`custom`](examples/custom): Shows how to set up a fully customized usage of the plugin.

Feel free to explore and adapt them to your project!

---

## See Also

- [GitLab Repository](https://gitlab.com/thiti-mkdocs-plugins/mkdocs-table-of-figures/)
- [MkDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Jinja2](https://jinja.palletsprojects.com/en/stable/)
- [MermaidJS](https://mermaid-js.github.io/mermaid/#/)
