---
layout: page
title: Courses
permalink: /courses/
---

{% assign schools = site.courses | map: "school" | uniq %}

{% for school in schools %}
{% assign school_courses = site.courses | where: "school", school %}
{% assign codes_unique = school_courses | map: "code" | uniq %}

Feel free to use the in-built browser search to find a specific course, if there are too many of them. Check out how to do it in
[Chrome](https://support.google.com/chrome/answer/95440?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Csearch-within-a-page),
[Firefox](https://support.mozilla.org/en-US/kb/search-contents-current-page-text-or-links) (
[Android](https://support.mozilla.org/en-US/kb/how-use-find-page-firefox-android) /
[iOS](https://support.mozilla.org/en-US/kb/search-within-web-page-firefox-ios) /
[Focus Android](https://support.mozilla.org/en-US/kb/find-words-page-firefox-focus-android) /
[Focus iOS](https://support.mozilla.org/en-US/kb/find-words-page-firefox-focus-ios)),
[Opera](https://help.opera.com/en/opera36/browse-the-web/),
[Safari](https://appleinsider.com/articles/21/04/09/how-to-search-website-content-from-within-safari).

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
