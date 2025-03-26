module.exports = async ({github, context, core, exec, io}) => {
  const fs = require('fs');

  const issue = await github.rest.issues.get({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: context.issue.number
  });
  
  const body = issue.data.body;
  
  const regexSchool = /^- school: (.+)$/m;
  const regexCode = /^- code: (.+)$/m;
  const regexSemester = /^- semester: (.+)$/m;
  const regexType = /^- exam type: (.+)$/m;
  const regexName = /^- name: (.+)$/m;
  const regexDate = /^- date: (.+)$/m;
  const regexGrade = /^- grade: (\d+(?:\.\d+)?) people: (\d+)( #.*)?$/mg;
  const matchSchool = body.match(regexSchool)[1].trim();
  const matchCode = body.match(regexCode)[1].trim().toUpperCase();
  const matchSemester = body.match(regexSemester)[1].trim().toUpperCase();
  const matchType = body.match(regexType)[1].trim().toLowerCase();
  const matchName = body.match(regexName)[1].trim();
  const matchDate = body.match(regexDate)[1].trim();

  const regexEcts = /^- ects: (\d+)$/m;
  const regexHours = /^- semester hours: (\d+)$/m;
  const regexMode = /^- mode: (.+)$/m;
  const regexLang = /^- language: (.+)$/m;
  const matchEcts = body.match(regexEcts)[1].trim();
  const matchHours = body.match(regexHours)[1].trim();
  const matchMode = body.match(regexMode)[1].trim().toLowerCase();
  const matchLang = body.match(regexLang)[1].trim().toLowerCase();

  const matchGrades = Array.from(body.matchAll(regexGrade)).map((match) => { return { 'grade': match[1], 'people': match[2] }; });
  const literalDesc = '## Description';
  const matchDesc = body.substring(body.indexOf(literalDesc) + literalDesc.length).trim();
  const fileContent = `---
layout: course

school: "${matchSchool}"
code: "${matchCode}"
semester: "${matchSemester}" # refers to the year of the semester start
exam_type: "${matchType}"
name: "${matchName}"
date: "${matchDate}"

ects: ${matchEcts}
hours: ${matchHours} # semester hours
mode: "${matchMode}"
lang: "${matchLang}"

title: "${matchName} ${matchSemester} ${matchType.charAt(0).toUpperCase() + matchType.slice(1)}"
${matchGrades.length > 0 ? 'grades:\r\n' + matchGrades.map((match) => `  - { grade: ${match.grade}, people: ${match.people} }`).join('\r\n') : ''}
---

${matchDesc}
`;

  const folderPath = `./_courses/${matchSchool}/${matchCode}`;
  await io.mkdirP(folderPath);

  core.info(`Created path "${folderPath}/".`);

  const filePath = `${folderPath}/${matchSemester}-${matchType}.md`;
  
  fs.writeFileSync(filePath, fileContent);

  core.notice(`Locally added course "${filePath}".`);
  
  return filePath;
}