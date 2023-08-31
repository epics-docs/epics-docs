from docutils import nodes
from docutils.parsers.rst.roles import set_classes

from sphinx.directives.other import TocTree, int_or_nothing
from docutils.parsers.rst import directives
from sphinx import addnodes
from copy import deepcopy


def extra_label_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Specific labels role for EPICS Documentation

    Returns tuple containing list of nodes to insert into the
    document and a list of system messages.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    try:
        extra_labels = inliner.document.settings.env.app.config.extra_labels
        assert isinstance(extra_labels, dict)
    
        label_config = extra_labels.get(name)
        assert isinstance(label_config, dict)
        set_classes(options)
    
        node = nodes.emphasis(rawtext='', text='', **options)
        node['classes'].append('extra-label')

        node_1 = nodes.strong(raw=rawtext, text=label_config.get('label', name), **options)
        node_1['classes'].append('label')
        
        node_2 = nodes.emphasis(rawtext=rawtext, text=text, **options)

        node += node_1
        node += node_2

        env = inliner.document.settings.env
        if not hasattr(env, "doc_extralabels"):
            extralabel = dict()
            extralabel[env.docname] = dict()

            extralabel[env.docname][name] = [text]
            setattr(env, "doc_extralabels", extralabel)

        if env.docname not in env.doc_extralabels:
            env.doc_extralabels[env.docname] = dict()

        env.doc_extralabels[env.docname][name] = [text.strip() for text
                                                 in text.split(",")]
    except AssertionError:
        msg = inliner.reporter.error(
            'Cannot create label "%s". Please check "extra_labels" in conf.py' % name, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    return [node, ], []


class ExtraLabelTree(TocTree):
    """
    Extended Toc Tree class to allow filtering by the extra labels specified
    Directive extends the base Sphinx TocTree class.
    Add information about the meta label used in the document.
    Feature this work as a filter, that shows only this
    document that has the specific meta lebel in the content.
    """

    option_spec = {
        'maxdepth': int,
        'name': directives.unchanged,
        'caption': directives.unchanged_required,
        'glob': directives.flag,
        'hidden': directives.flag,
        'includehidden': directives.flag,
        'numbered': int_or_nothing,
        'titlesonly': directives.flag,
        'reversed': directives.flag,
        # add new filter options, it uses python notation
        # e.q {"audience": ["administrators", "all"]}
        'extralabel': str
    }

    def run(self):
        result = super(ExtraLabelTree, self).run()

        if "extralabel" not in self.options:
            return result

        env = self.state.document.settings.env
        if not hasattr(env, 'tocs_extralabel'):
            env.tocs_extralabel = dict()

        toc_extralabel = eval(self.options["extralabel"])
        env.tocs_extralabel[env.docname] = toc_extralabel

        for node in result:
            if hasattr(node, 'traverse'):
                for toctree_node in node.traverse(addnodes.toctree, include_self=True, siblings=True):
                    toctree_node['extralabel'] = toc_extralabel

        return result


def filtered_process(app, doctree, docname):
    """
    Filter the entries in the toctree for specific extra labels

    :param app: reference to the Sphinx application
    :param doctree: reference to the resolved doctree
    :param docname: name of the resolved document
    :return:
    """
    env = app.builder.env
    builder = app.builder
    if not hasattr(env, 'tocs'):
        return

    if not hasattr(env, 'tocs_extralabel'):
        return

    def _filter_all_toctrees():
        """"
        Method used to filter all toctrees that use ExtraLabelTree features
        """
        for toc_name, _filter in env.tocs_extralabel.items():
            toctree = env.tocs[toc_name][0][1][0]
            _filter_the_toctree(toctree, _filter)

    def _filter_the_toctree(toctree, _filter):
        """
        Method used to filter specific toctrees

        :param toctree: the toctree to filter
        :param _filter: the configuration dict use to filtering
        :return:
        """
        entries = toctree["entries"]
        parsed_entries = []

        for ent in entries:
            ent_name = ent[1]

            if ent_name in env.doc_extralabels:
                ent_extralabels = env.doc_extralabels[ent_name]

                _add = [False for _ in range(len(_filter.keys()))]
                index = 0

                for index, key in enumerate(_filter.keys()):
                    filter_values = _filter[key]
                    if type(filter_values) is not list:
                        filter_values = [filter_values]

                    for filter_value in filter_values:
                        try:
                            if filter_value in ent_extralabels[key]:
                                _add[index] = True
                                break
                        except KeyError:
                            break

                if all(_add):
                    parsed_entries.append((None, ent_name))

        toctree["entries"] = parsed_entries

    if docname.__eq__(env.config.master_doc):
        _filter_all_toctrees()

    elif docname in env.tocs_extralabel.keys():
        # make backup of already parsed ToC, before we modify it
        tocs_origin = deepcopy(env.tocs)

        # process toctrees in the doc
        for toctree in doctree.traverse(addnodes.toctree):
            label = toctree['extralabel']
            # filter this toctree and all ist subtrees.
            _filter_the_toctree(toctree, label)
            for subtoctree in toctree.traverse(addnodes.toctree,
                                               include_self=False,
                                               siblings=True):
                _filter_the_toctree(subtoctree, label)

            # filter all other tocs entries
            for doc, toc in env.tocs.items():
                for subtoctree in toc.traverse(addnodes.toctree,
                                               include_self=False,
                                               siblings=True):
                    _filter_the_toctree(subtoctree, label)

            # resolve toctree to bullet list and replace it
            # to avoid default processing
            result = env.resolve_toctree(docname, builder, toctree)
            if result is None:
                toctree.replace_self([])
            else:
                toctree.replace_self(result)

        # revert ToC from backup
        env.tocs = tocs_origin


def setup(app):
    """Install the plugin.

    :param app: Sphinx application context.
    """
    app.add_config_value('extra_labels', None, 'env')

    extra_labels = app.config._raw_config.get('extra_labels', {})
    assert isinstance(extra_labels, dict)

    for key in extra_labels.keys():
        app.add_role(key, extra_label_role)

    directives.register_directive('toctree', ExtraLabelTree)
    app.connect("doctree-resolved", filtered_process)

    return {'version': '0.1.0'}
