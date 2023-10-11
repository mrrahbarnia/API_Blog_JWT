{% extends "mail_templated/base.tpl" %}

{% block subject %}
Hello
{% endblock %}


{% block html %}
<a href={{context}}><h3>Click here</h3></a>
{% endblock %}