from docutils import nodes
from docutils.parsers.rst.roles import set_classes

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


def setup(app):
    """Install the plugin

    :param app: Sphinx application context.
    """
    app.add_config_value('extra_labels', None, 'env')

    extra_labels = app.config._raw_config.get('extra_labels', {})
    assert isinstance(extra_labels, dict)

    for key in extra_labels.keys():
        app.add_role(key, extra_label_role)

    return {'version': '0.1.0'}
