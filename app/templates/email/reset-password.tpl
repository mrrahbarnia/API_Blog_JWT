{% extends "mail_templated/base.tpl" %}

{% block subject %}
Hello
{% endblock %}


{% block html %}
{{token}}
<p>Please copy this token and paste it in below link for validation process.</p>
<a href={{link}}><h3>link</h3></a>
{% endblock %}