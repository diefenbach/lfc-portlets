# python imports
import random

# django imports
from django import forms
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


# tagging imports
import tagging.utils
from tagging.forms import TagField

# portlets imports
from portlets.models import Portlet

# lfc imports
import lfc.utils
from lfc.models import BaseContent
from lfc.fields.autocomplete import AutoCompleteTagInput
from lfc.fields.wysiwyg import WYSIWYGInput


class NavigationPortlet(Portlet):
    """A portlet to display the navigation tree.

    Note: this reuses mainly the navigation inclusion tag.

    Parameters:

        - start_level:
            The tree is displayed from this level 1. The tree starts with 1

        - expand_level:
            The tree is expanded up this level. Default is 0, which means the
            tree is not expanded at all but the current node.
    """
    start_level = models.PositiveSmallIntegerField(default=1)
    expand_level = models.PositiveSmallIntegerField(default=0)

    def render(self, context):
        """Renders the portlet as HTML.
        """
        request = context.get("request")
        return render_to_string("lfc/portlets/navigation_portlet.html", RequestContext(request, {
            "start_level": self.start_level,
            "expand_level": self.expand_level,
            "title": self.title,
        }))

    def form(self, **kwargs):
        """
        """
        return NavigationPortletForm(instance=self, **kwargs)


class NavigationPortletForm(forms.ModelForm):
    """Add/edit form for the navigation portlet.
    """
    class Meta:
        model = NavigationPortlet


class ContentPortlet(Portlet):
    """A portlet to display arbitrary content objects. The objects can be
    selected by tags.

    **Attributes:**

    limit:
        The amount of objects which are displayed at maximum.

    tags:
        The tags an object must have to be displayed.
    """
    limit = models.PositiveSmallIntegerField(default=5)
    tags = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as HTML.
        """
        request = context.get("request")
        temp = BaseContent.objects.filter(
            language__in=("0", translation.get_language()))

        if self.tags:
            temp = tagging.managers.ModelTaggedItemManager().with_all(self.tags, temp)[:self.limit]
        else:
            temp = temp[:self.limit]

        objs = []
        for obj in temp:
            obj = obj.get_content_object()
            if lfc.utils.registration.get_info(obj) and obj.has_permission(request.user, "view") and obj.is_active(request.user):
                objs.append(obj)

        return render_to_string("lfc/portlets/content_portlet.html", {
            "title": self.title,
            "objs": objs,
        })

    def form(self, **kwargs):
        """Returns the add/edit form of the portlet.
        """
        return ContentPortletForm(instance=self, **kwargs)


class ContentPortletForm(forms.ModelForm):
    """Add/edit form of the content portlet.
    """
    tags = TagField(widget=AutoCompleteTagInput(), required=False)

    class Meta:
        model = ContentPortlet


class RandomPortlet(Portlet):
    """A portlet to display random objects. The objects can be selected by
    tags.

    **Attributes:**

    limit:
        The amount of objects which are displayed at maximum.

    tags:
        The tags an object must have to be displayed.
    """
    limit = models.PositiveSmallIntegerField(default=1)
    tags = models.CharField(blank=True, max_length=100)

    def render(self, context):
        """Renders the portlet as HTML.
        """
        items = BaseContent.objects.filter(
            language__in=("0", translation.get_language()))

        if self.tags:
            items = tagging.managers.ModelTaggedItemManager().with_all(self.tags, items)[:self.limit]

        items = list(items)
        random.shuffle(items)

        return render_to_string("lfc/portlets/random_portlet.html", {
            "title": self.title,
            "items": items[:self.limit],
        })

    def form(self, **kwargs):
        """Returns the form of the portlet.
        """
        return RandomPortletForm(instance=self, **kwargs)


class RandomPortletForm(forms.ModelForm):
    """Add/Edit form for the random portlet.
    """
    tags = TagField(widget=AutoCompleteTagInput(), required=False)

    class Meta:
        model = RandomPortlet


class TextPortlet(Portlet):
    """A portlet to display arbitrary HTML text.

    **Attributes:**

    text:
        The HTML text which is displayed. Can contain any HTML text.
    """

    text = models.TextField(_(u"Text"), blank=True)

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as HTML.
        """
        return render_to_string("lfc/portlets/text_portlet.html", {
            "title": self.title,
            "text": self.text
        })

    def form(self, **kwargs):
        """
        """
        return TextPortletForm(instance=self, **kwargs)


class TextPortletForm(forms.ModelForm):
    """Add/Edit form for the text portlet.
    """
    class Meta:
        model = TextPortlet

    def __init__(self, *args, **kwargs):
        super(TextPortletForm, self).__init__(*args, **kwargs)
        self.fields["text"].widget = WYSIWYGInput()
