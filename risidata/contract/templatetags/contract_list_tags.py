from django import template
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.templatetags.base_list_tags import ResultList, InclusionSiteNode
from core.utils import (
    has_permission_add,
    has_permission_view,
    get_slug_url,
    label_for_field, try_get_url,
)

register = template.Library()


def result_headers(cl):
    """Создание заголовков столбцов таблицы"""
    for column in cl.columns:
        field = cl.model._meta.get_field(column)
        if (
                field.remote_field
                and not isinstance(field.remote_field, models.ManyToOneRel)
                and not has_permission_view(cl.request, field.related_model)
        ):
            continue
        text = label_for_field(column, cl.model, cl.form_class)
        yield {"text": text}


def results(cl):
    for res in cl.result_list:
        yield ResultList(None, columns_list_result(cl, res))


def result_list(cl):
    return {
        "cl": cl,
        "result_headers": list(result_headers(cl)),
        "results": list(results(cl)),
    }


@register.tag(name="result_list")
def result_list_tag(parser, token):
    return InclusionSiteNode(
        parser,
        token,
        func=result_list,
        template_name="cl_results.html",
        takes_context=False,
    )


def columns_list_result(cl, res):
    empty_value_display = cl.model_view.get_empty_value_display()
    number = str(res)
    app_label = cl.model_view.app_label

    for i, field_name in enumerate(cl.columns):
        if i == 0:
            kwargs = {'slug': get_slug_url({}, cl.model, res.id)}
            url_obj = try_get_url(f'{app_label}_change', kwargs, app_label)
            link = format_html(
                '<a href="{}"{}>{}</a>',
                url_obj,
                mark_safe(' class="empty"') if not res.number else '',
                number
            )
            yield format_html(f'<th>{link}</th>')
        else:
            field = res._meta.get_field(field_name)
            if (
                    field.remote_field is None
                    or isinstance(field.remote_field, models.ManyToOneRel)
            ):
                value = getattr(res, field.name)
                text = value if value else empty_value_display
                yield format_html(f'<td>{text}</td>')

            else:
                model = field.related_model
                if not has_permission_view(cl.request, model):
                    continue
                opts = model._meta
                kwargs = {'slug': get_slug_url({}, model, related_id=res.id)}

                if isinstance(field, models.OneToOneRel):
                    url_obj = try_get_url(
                        f'{app_label}_change', kwargs, app_label
                    )
                    title = format_html(
                        '{} договора {}',
                        opts.verbose_name_plural.lower(),
                        number,
                    )
                    link_list = format_html(
                        '<a href="{}" title="{}">{}</a>',
                        url_obj,
                        title,
                        opts.verbose_name_plural.lower(),
                    )
                    yield format_html(f'<td>{link_list}</td>')

                elif isinstance(field, models.ManyToOneRel):
                    url_obj = try_get_url(
                        f'{app_label}_list', kwargs, app_label
                    )
                    title_list = format_html('{} договора {}',
                                             opts.verbose_name_plural.lower(),
                                             number)
                    verbose_name = getattr(model, 'verbose_name_plural_short',
                                           opts.verbose_name_plural.lower())
                    link_list = format_html(
                        '<a href="{}" title="{}">{}</a>{}',
                        url_obj,
                        title_list,
                        verbose_name,
                        mark_safe('&emsp;')
                    )
                    if has_permission_add(cl.request, model):
                        url_add = try_get_url(
                            f'{app_label}_add', kwargs, app_label
                        )
                        title_add = format_html(
                            'Добавить {} к договору {}',
                            opts.verbose_name.lower(),
                            number,
                        )
                        link_add = format_html(
                            '<a href="{}" title="{}">'
                            '<img src="{}" alt="Добавить"></a>',
                            url_add,
                            title_add,
                            '/static/contract/img/icon-addlink.svg'
                        )
                    else:
                        link_add = ''

                    check = model.objects.filter(
                            models.Q((cl.opts.model_name, res),)
                    ).exists()
                    yield format_html(
                        '<td><div class="nowrap">'
                        '<span class="nowrap">{}</span>{}</div></td>',
                        link_list if check else '',
                        link_add,
                    )
