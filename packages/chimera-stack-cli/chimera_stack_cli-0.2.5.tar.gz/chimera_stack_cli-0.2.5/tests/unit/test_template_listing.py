from chimera.core import TemplateManager


def test_frontend_visible():
    tpls = TemplateManager().get_templates_by_category()
    assert any(t['id'].startswith('stacks/frontend/')
               for t in tpls.get('frontend', []))
