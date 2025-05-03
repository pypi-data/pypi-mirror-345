# Sphinx Reference Graph

## Introduction

This package contains a Sphinx extension for generating and inserting an interactive graph based on internal references and the table of content. A user can tweak the graph to suit their needs. The graph has clickable nodes that link to pages within the Jupyter book.

## What does it do?

Based on the internal references, the table of content, the directives mentioned below and the provided extension options, a graph is generated, where each node represents a page within the book and each link between two nodes represents a reference between the corresponding pages.

Each node/page can be assigned a tag. All nodes with the same tag will have the same color and, if three or more nodes have the same tag, an extended convex hull will be drawn around nodes with the same tag.

This extension provides several Sphinx directives:

- `refgraph`:
  - This directive inserts the generated graph at the specified location.
- `refgraphtag`:
  - This directive can be used to assign a tag to a page, which will be used in the graph to group nodes together.
- `refgraphhidden`:
  - This directive can be used to include hidden references, to force edges in the graph.
- `refgraphignore`:
  - This directive can be used to remove the relevant node entirely from the graph.

## Installation

To use this extension, follow these steps:

**Step 1: Install the Package**

Install the module `sphinx-ref-graph` package using `pip`:
```
pip install git+https://github.com/TeachBooks/Sphinx-ref-graph.git
```
    
**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
git+https://github.com/TeachBooks/Sphinx-ref-graph.git
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of Sphinx extra extensions (**important**: underscore, not dash this time):
```
sphinx: 
    extra_extensions:
        .
        .
        .
        - sphinx_ref_graph
        .
        .
        .
```

## Configuration

The extension provides several configuration values, which can be added to `_config.yml`:

```yaml
sphinx: 
    config:
        -
        -
        -
        ref_graph_temp_file:      ref_graph.temp # default value
        ref_graph_html_file:      ref_graph.html # default value
        ref_graph_internal_links: true           # default value
        ref_graph_toc_links:      true           # default value
        ref_graph_tag_color:      {}             # default value
        ref_graph_remove_links:   []             # default value
        ref_graph_group_nodes:    false          # default value
        ref_graph_collapse_group: false          # default value
        -
        -
        -
```

An explanation of each configuration value:

- `ref_graph_temp_file`: `ref_graph.temp` (_default_) or **string**:
  - The name of the (temporary) file used to store the information about nodes, tags and links.
- `ref_graph_html_file`: `ref_graph.html` (_default_) or **string**:
  - The name of the `html` file that will contain the generated graph. This file will be included using an iframe at the required locations.
- `ref_graph_internal_links`: `true` (_default_) or `false`:
  - If `true`, all internal references defined in pages of the book will result in a link in the graph.
  - If `false`, all internal references defined in pages of the book will be ignored, including hidden internal references.
- `ref_graph_toc_links`: `true` (_default_) or `false`:
  - If `true`, all references defined in table of content of the book will result in a link in the graph.
  - If `false`, all references defined in table of content of the book will be ignored, including hidden internal references.
  - For details about defining references in the table of content, see [Provided code](#provided-code).
- `ref_graph_tag_color`: `{}` (_default_) or **Python dictionary**:
  - The **Python dictionary** must be empty or contain key-value pairs of the form `'tag':'color'`, where `'color'` should be a JavaScript recognized color, preferably a hex RGB color.
  - If set to a non-empty dictionary, all nodes with the same tag will be given the provided color and for tags with three or more nodes the extended convex hull will be drawn in the same color.
  - For all tags that are not a key in this value, a color will be selected cyclically from the set of colors:
    ```python
    "#6F1D77", # Light Purple
    "#0C2340", # Dark Blue
    "#EC6842", # Orange
    "#0076C2", # Royal Blue
    "#E03C31", # Red
    "#00B8C8", # Turquoise
    "#EF60A3", # Pink
    "#009B77", # Forrest Green
    "#A50034", # Burgundy
    ```
    The order in which the tags are encountered defines the order in which the colors are selected.
  - An example:
    ```yaml
    ref_graph_tag_color: {'Eigenvalues':'#900bee','Matrix operations':'#0cd734'}
    ```
- `ref_graph_remove_links`: `[]` (_default_) or **Python list**:
  - The **Python list** must contain **Python strings**, where each is of the form `"file1 -> file2"`.
  - In the above, `file1` and `file2` must be the paths to `html` files in the compiled book. The paths are assumed to be relative to the main location of the html files of the compiled book.
  - If not empty, each of the entered links will be removed from the graph.
  - An example:
    ```yaml
    ref_graph_remove_links: ['Introduction.html -> Colophon/Acknowledgements.html']
    ```
- `ref_graph_group_nodes`: `false` (_default_) or `true`:
  - If `true`, for each tag an extra node will be added.
  - All other nodes with the same tag will obtain a link to this new node.
  - All links pointing to/from another node with the same tag will be altered to point to/from the new node.
  - The new node will not be clickable.
- `ref_graph_collapse_group`: `false` (_default_) or `true`:
  - If `True`, similar to ref_graph_group_nodes.
  - In addition all other nodes with the same tag will be removed from the graph.

## Provided code

### Directives

#### `refgraph`

The directive `refgraph` can be used to _show_ the generated graph. The graph does not depend on the location of this directive and will always be generated. Example code:

```md
:::{refgraph}
:::
```

This directive has the additional option `class`, of which the value will be added to the class of the iframe that is used to show the graph. Example code:

```md
:::{refgraph}
:class: dark-light
:::
```

#### `refgraphtag`

The directive `refgraphtag` can be used to assign a tag to a page, which will be used in the graph to group nodes together. Example code:

```md
:::{refgraphtag} Eigenvalues
:::
```

This directive has no options, nor will show in the page itself. The mandatory first (and only) argument is the tag that will be used.

#### `refgraphhidden`

The directive `refgraphhidden` can be used to include hidden references, to force edges in the graph. Example code:

```md
:::{refgraphhidden}
{doc}`/Chapter1/Vectors`
{ref}`Sec:LinesAndPlanes`
{numref}`Sec:DetExtras`
{prf:ref}`Dfn:DetExtras:VolumeRn`
:::
```

This directive has no options, nor arguments, nor will show in the page itself. The included references will however be present in the form of links in the generated graph.

#### `refgraphignore`

The directive `refgraphignore` can be used to remove the relevant node entirely from the graph. Example code:
```md
:::{refgraphignore}
:::
```

This directive has no options, nor arguments, nor will show in the page itself. The relevant node and all links to this node will be removed from the graph.

### Code in table of contents

> [!CAUTION]
> The next approach might be considered a _bad practice_. The authors of this extension claim in no way that this is not the case, but however have opted for this option to provide an alternative to directives.

Within the file `_toc.yml` a user can add a comment behind each line referencing a source file. If this comment contains the text
```yaml
ref_graph: {...}
```
this extension will parse this comment. `{...}` should be a **Python dictionary**.

Allowed keys for this dictionary are:

- `'tag'`:
  - The value assigned to this key will be the tag assigned to page in the ToC.
  - Example:
    ```yaml
    - file: 'Chapter1/Vectors.md'  # ref_graph: {'tag': 'Vectors, Lines and Planes'}
    ```
    This will assign the tag `Vectors, Lines and Planes` to the page `Chapter1/Vectors.html`.
    The alternative with directives is to add
    ```md
    :::{refgraphtag} Vectors, Lines and Planes
    :::
    ```
    to the file `Chapter1/Vectors.md`.
- `'refs'`:
  - The value should be a **Python list of strings**.
  - The value assigned to this key will be used to define a hidden reference from the page in the ToC to the page(s) in the value.
  - Example:
    ```yaml
    - file: 'Chapter6/ComplexEigenvalues.md' # ref_graph: {'refs':['Appendices/ComplexNumbers.md']}
    ```
    This will create a link in the graph between the nodes related to the pages `Chapter6/ComplexEigenvalues.html` and `Appendices/ComplexNumbers.html`.
    The alternative with directives is to add
    ```md
    :::{refgraphhidden}
    {doc}`Appendices/ComplexNumbers.md`
    :::
    ```
    to the file `Chapter6/ComplexEigenvalues.md`.
- `'ignore'`:
  - The value should be `True` or `False`.
  - If set to `True`, the relevant node will be entirely removed from the graph.
  - If set to any other value, nothing will happen.
  - Example:
    ```yaml
    - file: genindex.md # ref_graph: {'ignore':True}
    ```
    This will remove the node associated with `genindex.html` and any links in the graph to this node from the graph.
    The alternative with directives is to add
    ```md
    :::{refgraphignore}
    :::
    ```
    to the file `genindex.md`.

Any subset of these keys can be used in the comment.

> [!WARNING]
> Do not use `{` and/or `}` inside the keys and values in the **Python dictionary**, as the comment will be parsed as a string, where the first `{` after `ref_graph:` will be matched with the next `}`.

## Examples and details

An example of a page using this extension can be found at https://douden.github.io/openlabook/GoC.html.

## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/sphinx-ref-graph/). If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/sphinx-ref-graph/).

The `README.md` of the branch `manual` is also part of the [TeachBooks manual](https://teachbooks.io/manual).
