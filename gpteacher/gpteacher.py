"""
An XBlock that uses OpenAI's GPT natural language processing model to answer student questions
related to a specific topic. The XBlock displays a text input field where students can type their
questions, and sends each question to the GPT model via the OpenAI API. The model generates a response,
which is displayed to the student in the XBlock.
"""
import openai
import pkg_resources
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _


@XBlock.needs('i18n')
class GPTeacherXBlock(StudioEditableXBlockMixin, XBlock):
    """
    This XBlock provides a chat interface integrated with OpenAI's GPT
    """

    display_name = String(
        display_name=_("Display Name"),
        help=_(
            "Enter the name that students see for this component."
        ),
        default="GPTeacher",
        scope=Scope.settings
    )
    api_key = String(
        display_name=_("OpenAI API Key"),
        help=_(
            "Enter your OpenAI API Key. "
            "Go to https://platform.openai.com/account/api-keys to create one."
        ),
        default=None,
        scope=Scope.settings
    )
    hint = String(
        display_name=_("Topic Hint"),
        help=_(
            "Topics GPT will be answering. "
            "The more specific, the more efficient GPT will be in refusing unrelated questions."
        ),
        default=None,
        Scope=Scope.settings
    )
    model = String(
        display_name=_("GPT model"),
        help=_(
            "Select the GPT language model to use. "
            "Check https://platform.openai.com/docs/models for more options."
        ),
        default="gpt-3.5-turbo",
        Scope=Scope.settings
    )

    editable_fields = (
        'display_name', 'api_key', 'hint', 'model'
    )

    history = []

    def __init__(self, runtime, field_data, **kwargs):
        super(GPTeacherXBlock, self).__init__(runtime, field_data, **kwargs)

        openai.api_key = self.api_key

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        The primary view of the GPTeacher, shown to students
        when viewing courses.
        """
        if not self.api_key or not self.hint:
            return Fragment('<p>Set the OpenAI API Key and Hint</p>')
        html = self.resource_string("static/html/gpteacher.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/gpteacher.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(self.runtime.local_resource_url(self, statici18n_js_url))

        frag.add_javascript(self.resource_string("static/js/src/gpteacher.js"))
        frag.initialize_js('GPTeacherXBlock')
        return frag

    def studio_view(self, context=None):
        """
        Get Studio View fragment
        """
        return super(GPTeacherXBlock, self).studio_view(context)

    def _build_messages(self, user_input):
        """ Builds the message history including the prompt """
        self.history.append({'role': 'user', 'content': user_input})
        messages = [{
            'role': 'system',
            'content': f'You are GPTeacher, who is only allowed to answer questions related to {self.hint},'
                        ' refuse to answer anything else.'
        }] + self.history
        return messages

    @XBlock.json_handler
    def get_response(self, data, suffix=''):  # pylint: disable=unused-argument
        """ Sends prompt to ChatGPT and return results """
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self._build_messages(data['user_input'])
        )
        response = completion.choices[0].message.content
        self.history.append({'role': 'assistant', 'content': response})
        return {'response': str(response)}

    @staticmethod
    def _get_statici18n_js_url():
        """
        Returns the Javascript translation file for the currently selected language, if any.
        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = 'public/js/translations/{locale_code}/text.js'
        lang_code = locale_code.split('-')[0]
        for code in (locale_code, lang_code, 'en'):
            loader = ResourceLoader(__name__)
            if pkg_resources.resource_exists(
                    loader.module_name, text_js.format(locale_code=code)):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Dummy method to generate initial i18n
        """
        return translation.gettext_noop('Dummy')
