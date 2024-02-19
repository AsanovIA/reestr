import datetime

from django import template
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.contrib.admin.utils import (
    lookup_field, display_for_field, display_for_value
)
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.utils import (
    label_for_field, has_permission_view, get_slug_url, try_get_url,
    has_permission_add, label_for_column
)

register = template.Library()


class InclusionSiteNode(InclusionAdminNode):
    def render(self, context):
        context.render_context[self] = context.template.engine.select_template(
            [
                f'core/{self.template_name}',
            ]
        )
        return super(InclusionAdminNode, self).render(context)


def result_headers(cl):
    """Создание заголовков столбцов таблицы"""
    if hasattr(cl, 'columns'):
        for column in cl.columns:
            field = cl.model._meta.get_field(column)
            if (
                    field.remote_field
                    and not isinstance(field.remote_field, models.ManyToOneRel)
                    and not has_permission_view(cl.request,
                                                field.related_model)
            ):
                continue
            text = label_for_column(column, cl.model, form=cl.form)
            yield {"text": text}

    elif hasattr(cl, 'fields_display'):
        for i, field_name in enumerate(cl.fields_display):
            text, attr = label_for_field(
                field_name, cl.model, cl.model_view, True, cl.form)
            yield {"text": text}


class ResultList(list):
    def __init__(self, form, *items):
        self.form = form
        super().__init__(*items)


def results(cl):
    if cl.formset:
        for index in range(len(cl.formset.forms)):
            if index < cl.result_count:
                res = cl.result_list[index]
                form = cl.formset.forms[index]
                yield ResultList(form, items_for_result(cl, res, form))
            else:
                form = cl.formset.forms[index]
                yield ResultList(form, items_for_extra(cl, cl.model, form))
    elif hasattr(cl, 'columns'):
        for res in cl.result_list:
            yield ResultList(None, columns_list_result(cl, res))
    else:
        for res in cl.result_list:
            yield ResultList(None, items_for_result(cl, res))


def result_hidden_fields(cl):
    if cl.formset:
        for form in cl.formset.forms:
            if form[cl.opts.pk.name].is_hidden:
                yield mark_safe(form[cl.opts.pk.name])


def result_list(cl):
    return {
        "cl": cl,
        "result_hidden_fields": list(result_hidden_fields(cl)),
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


def items_for_result(cl, result, form=None):

    def link_in_col(is_first, field_name, cl):
        if cl.fields_link is None:
            return False
        if is_first and not cl.fields_link:
            return True
        return field_name in cl.fields_link

    first = True
    empty_value_display = cl.model_view.get_empty_value_display()
    for field_index, field_name in enumerate(cl.fields_display):
        row_classes = ["field-%s" % field_name]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_view)
            # f = result._meta.get_field(field_name)
            # value = getattr(result, field_name)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            if f is None:
                boolean = getattr(attr, "boolean", False)
                result_repr = display_for_value(
                    value, empty_value_display, boolean
                )
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(
                        value, f, empty_value_display
                    )
                if isinstance(
                        f,
                        (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")
        row_class = mark_safe(' class="%s"' % " ".join(row_classes))
        # If list_display_links not defined, add the link tag to the first field
        if link_in_col(first, field_name, cl):
            table_tag = "th" if first else "td"
            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                link_class = ''
                if not result_repr:
                    link_class = mark_safe("empty")
                    label = label_for_field(field_name, cl.model, form=cl.form)
                    result_repr = f'{label} отсутствует'

                link_or_text = format_html(
                    '<a href="{}"{}>{}</a>',
                    url,
                    format_html(' class="{}"', link_class)
                    if link_class
                    else '',
                    result_repr,
                )

            yield format_html(
                "<{}{}>{}</{}>", table_tag, row_class, link_or_text, table_tag
            )
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (
                form
                and field_name in form.fields
                and not (
                    field_name == cl.opts.pk.name
                    and form[cl.opts.pk.name].is_hidden
                )
            ):
                bf = form[field_name]
                result_repr = mark_safe(str(bf.errors) + str(bf))

            yield format_html(f'<td{row_class}>{result_repr}</td>')
    if form and not form[cl.opts.pk.name].is_hidden:
        yield format_html("<td>{}</td>", form[cl.opts.pk.name])


def items_for_extra(cl, result, form):

    def link_in_col(is_first, field_name, cl):
        if cl.fields_link is None:
            return False
        if is_first and not cl.fields_link:
            return True
        return field_name in cl.fields_link

    first = True
    empty_value_display = cl.model_view.get_empty_value_display()
    for field_index, field_name in enumerate(cl.fields_display):
        row_classes = ["field-%s" % field_name]
        try:
            f = result._meta.get_field(field_name)
            value = form.initial.get(field_name, empty_value_display)
            # value = getattr(result, field_name)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            if isinstance(f.remote_field, models.ManyToOneRel):
                field_val = form.initial.get(f.name, empty_value_display)
                # field_val = getattr(result, f.name)
                if field_val is None:
                    result_repr = empty_value_display
                else:
                    result_repr = field_val
            else:
                from django.contrib.admin.utils import display_for_field

                result_repr = display_for_field(value, f, empty_value_display)
            if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
            ):
                row_classes.append("nowrap")
        row_class = mark_safe(' class="%s"' % " ".join(row_classes))
        # If list_display_links not defined, add the link tag to the first field
        if link_in_col(first, field_name, cl):
            table_tag = "th" if first else "td"
            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result_repr)
                # url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                label = label_for_field(field_name, cl.model, form=cl.form)
                link_class = '' if result_repr else mark_safe("empty")
                result_repr = result_repr or f'{label} отсутствует'

                link_or_text = format_html(
                    '<a href="{}"{}>{}</a>',
                    url,
                    format_html(' class="{}"', link_class)
                    if link_class
                    else '',
                    result_repr,
                )

            yield format_html(
                "<{}{}>{}</{}>", table_tag, row_class, link_or_text, table_tag
            )
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (
                form
                and field_name in form.fields
                and not (
                    field_name == cl.opts.pk.name
                    and form[cl.opts.pk.name].is_hidden
                )
            ):
                bf = form[field_name]
                result_repr = mark_safe(str(bf.errors) + str(bf))

            yield format_html(f'<td{row_class}>{result_repr}</td>')
    if form and not form[cl.opts.pk.name].is_hidden:
        yield format_html("<td>{}</td>", form[cl.opts.pk.name])


def columns_list_result(cl, result):
    app_label = cl.model_view.app_label
    action = cl.model_view.action
    urlargs = {'action': action, 'current_app': app_label}
    empty_value_display = cl.model_view.get_empty_value_display()
    number = str(result)

    parent_model_name = cl.opts.verbose_name
    for i, field_name in enumerate(cl.columns):
        field = result._meta.get_field(field_name)
        if (
                field.remote_field is None
                or (field.is_relation and field.many_to_one
                    and field.related_model)
        ):
            model = cl.model
            if i == 0:
                urlargs.update(slug=get_slug_url({}, model, result.id))
                url_obj = try_get_url(f'{app_label}_change', **urlargs)
                link = format_html(
                    '<a href="{}"{}>{}</a>',
                    url_obj,
                    mark_safe(' class="empty"') if not result.number else '',
                    number
                )
                yield format_html(f'<th>{link}</th>')
                continue

            value = getattr(result, field.name)
            text = value if value else empty_value_display
            yield format_html(f'<td>{text}</td>')

        elif field.is_relation and (field.one_to_many or field.one_to_one):
            model = field.related_model
            if not has_permission_view(cl.request, model):
                continue
            opts = model._meta

            if field.is_relation and field.one_to_one:
                urlargs.update(
                    slug=get_slug_url({}, model, result.id, result.id))
                url_obj = try_get_url(f'{app_label}_change', **urlargs)
                title = format_html('{} {}а {}',
                                    opts.verbose_name_plural.lower(),
                                    parent_model_name,
                                    number)
                link_list = format_html('<a href="{}" title="{}">{}</a>',
                                        url_obj,
                                        title,
                                        opts.verbose_name_plural.lower())
                yield format_html(f'<td>{link_list}</td>')

            elif field.is_relation and field.one_to_many:
                urlargs.update(
                    slug=get_slug_url({}, model, related_id=result.id))
                check = result.pk in cl.check[opts.model_name]
                if not check and action == 'view':
                    yield format_html(f'<td>{empty_value_display}</td>')
                    continue

                url_obj = try_get_url(f'{app_label}_list', **urlargs)
                title_list = format_html('{} {}а {}',
                                         opts.verbose_name_plural.lower(),
                                         parent_model_name,
                                         number)
                verbose_name = getattr(model, 'verbose_name_plural_short',
                                       opts.verbose_name_plural.lower())
                link_list = format_html('<a href="{}" title="{}">{}</a>{}',
                                        url_obj,
                                        title_list,
                                        verbose_name,
                                        mark_safe('&emsp;'))
                if (
                        has_permission_add(cl.request, model)
                        and action != 'view'
                ):
                    url_obj = try_get_url(f'{app_label}_add', **urlargs)
                    title_add = format_html('добавить {} к {}у {}',
                                            opts.verbose_name.lower(),
                                            parent_model_name,
                                            number)
                    link_add = format_html(
                        '<a href="{}" title="{}">'
                        '<img src="{}" alt="Добавить"></a>',
                        url_obj,
                        title_add,
                        '/static/contract/img/icon-addlink.svg'
                    )
                else:
                    link_add = ''

                yield format_html(
                    '<td><div class="nowrap">'
                    '<span class="nowrap">{}</span>{}</div></td>',
                    link_list if check else '',
                    link_add,
                )

        # f, attr, value = lookup_field(field_name, res, cl.model_view)
        # if field.is_relation and (field.one_to_many or field.one_to_one):
        #     model = field.related_model
        # else:
        #     model = cl.model
        #
        # if i == 0:
        #     kwargs = {'slug': get_slug_url({}, cl.model, res.id)}
        #     url_obj = try_get_url(f'{app_label}_change', kwargs, app_label)
        #     link = format_html(
        #         '<a href="{}"{}>{}</a>',
        #         url_obj,
        #         mark_safe(' class="empty"') if not res.number else '',
        #         number
        #     )
        #     yield format_html(f'<th>{link}</th>')
        #     continue
        #
        # # field = res._meta.get_field(field_name)
        # if (
        #         field.remote_field is None
        #         or isinstance(field.remote_field, models.ManyToOneRel)
        # ):
        #     value = getattr(res, field.name)
        #     text = value if value else empty_value_display
        #     yield format_html(f'<td>{text}</td>')
        #
        # else:
        #     # model = field.related_model
        #     if not has_permission_view(cl.request, model):
        #         continue
        #     opts = model._meta
        #     kwargs = {'slug': get_slug_url({}, model, related_id=res.id)}
        #
        #     if isinstance(field, models.OneToOneRel):
        #         url_obj = try_get_url(
        #             f'{app_label}_change', kwargs, app_label
        #         )
        #         title = format_html(
        #             '{} {}а {}',
        #             opts.verbose_name_plural.lower(),
        #             parent_model_name,
        #             number,
        #         )
        #         link_list = format_html(
        #             '<a href="{}" title="{}">{}</a>',
        #             url_obj,
        #             title,
        #             opts.verbose_name_plural.lower(),
        #         )
        #         yield format_html(f'<td>{link_list}</td>')
        #
        #     elif isinstance(field, models.ManyToOneRel):
        #         url_obj = try_get_url(
        #             f'{app_label}_list', kwargs, app_label
        #         )
        #         title_list = format_html('{} {}а {}',
        #                                  opts.verbose_name_plural.lower(),
        #                                  parent_model_name,
        #                                  number)
        #         verbose_name = getattr(model, 'verbose_name_plural_short',
        #                                opts.verbose_name_plural.lower())
        #         link_list = format_html(
        #             '<a href="{}" title="{}">{}</a>{}',
        #             url_obj,
        #             title_list,
        #             verbose_name,
        #             mark_safe('&emsp;')
        #         )
        #         if has_permission_add(cl.request, model):
        #             url_add = try_get_url(
        #                 f'{app_label}_add', kwargs, app_label
        #             )
        #             title_add = format_html(
        #                 'Добавить {} к {}у {}',
        #                 opts.verbose_name.lower(),
        #                 parent_model_name,
        #                 number,
        #             )
        #             link_add = format_html(
        #                 '<a href="{}" title="{}">'
        #                 '<img src="{}" alt="Добавить"></a>',
        #                 url_add,
        #                 title_add,
        #                 '/static/contract/img/icon-addlink.svg'
        #             )
        #         else:
        #             link_add = ''
        #
        #         check = model.objects.filter(
        #                 models.Q((cl.opts.model_name, res),)
        #         ).exists()
        #         yield format_html(
        #             '<td><div class="nowrap">'
        #             '<span class="nowrap">{}</span>{}</div></td>',
        #             link_list if check else '',
        #             link_add,
        #         )
