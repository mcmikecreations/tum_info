module.exports = async ({github, context, core}) => {
  const issue = await github.rest.issues.get({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: context.issue.number
  });
  console.log(issue);
  core.exportVariable('iss', issue);
  return issue;
}