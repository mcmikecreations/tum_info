---
layout: page
title: Courses
permalink: /courses/
---

{% assign schools = site.courses | map: "school" | uniq %}

{% for school in schools %}
{% assign school_courses = site.courses | where: "school", school %}
{% assign codes_unique = school_courses | map: "code" | uniq %}

### {{ school }}

{% for code in codes_unique %}
{% assign code_courses = school_courses | where: "code", code %}
{% assign code_semesters = code_courses | map: "semester" | uniq | sort | reverse %}
- {{ code }} {{ code_courses.first.name }}:
    {% for semester in code_semesters %}
    {% assign semester_courses = code_courses | where: "semester", semester %}
    - {{ semester }} {% for course in semester_courses %}[{{ course.exam_type | capitalize }}]({{ site.baseurl }}{{ course.url }}){% if forloop.last != true %}, {% endif %}{% endfor %}
    {% endfor %}
{% endfor %}

{% endfor %}
