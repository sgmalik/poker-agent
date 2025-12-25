## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (no functional changes, code improvements)
- [ ] Documentation update
- [ ] Test improvements
- [ ] Performance improvement

## Motivation and Context

<!-- Why is this change required? What problem does it solve? -->
<!-- If it fixes an open issue, please link to the issue here -->

Fixes #(issue)

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Poker Logic Changes (if applicable)

<!-- If this PR affects poker calculations, hand evaluation, ranges, or equity -->

- [ ] Hand evaluation logic
- [ ] Equity calculations
- [ ] Range operations
- [ ] GTO principles
- [ ] Other poker-specific logic:

**Validation**: <!-- How did you verify poker logic correctness? -->

## Testing

### Test Coverage

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All existing tests pass
- [ ] Test coverage maintained or improved

### Manual Testing

<!-- Describe manual testing performed -->

```bash
# Commands used for testing
pytest tests/
```

**Test Results**: <!-- Paste relevant test output or screenshots -->

## Code Quality Checklist

- [ ] Code follows project style guidelines
- [ ] Code formatted with `black`
- [ ] Linting passes with `ruff`
- [ ] Type checking passes with `pyrefly`
- [ ] Docstrings added for new public functions/classes
- [ ] No hardcoded secrets or API keys
- [ ] Error handling is appropriate
- [ ] Logging added for important operations

## Documentation

- [ ] README updated (if needed)
- [ ] API documentation updated (if needed)
- [ ] Inline code comments added where necessary
- [ ] SYSTEM_DESIGN.md updated (for architectural changes)

## Performance Considerations

<!-- Does this change affect performance? How? -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance degraded (justification required)

**Details**:

## Security Considerations

<!-- Does this change affect security? -->

- [ ] No security impact
- [ ] Input validation added/updated
- [ ] Authentication/authorization changes
- [ ] Sensitive data handling

**Details**:

## Screenshots (if applicable)

<!-- Add screenshots for UI changes or visual improvements -->

## Deployment Notes

<!-- Any special deployment considerations? Database migrations? Environment variables? -->

- [ ] No special deployment steps required
- [ ] Database migrations included
- [ ] New environment variables required (documented in .env.example)
- [ ] Dependencies added (requirements.txt updated)

## Reviewer Checklist

<!-- For the reviewer -->

- [ ] Code is clear and maintainable
- [ ] Tests are comprehensive
- [ ] No obvious bugs or issues
- [ ] Poker logic is correct (if applicable)
- [ ] Documentation is adequate
- [ ] Performance is acceptable
- [ ] Security considerations addressed

## Additional Notes

<!-- Any additional information for reviewers -->
