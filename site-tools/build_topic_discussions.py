"""Generate the Commons discussion pages from the existing topic cards."""
from pathlib import Path
import re

DOCS = Path(__file__).resolve().parents[1] / 'docs'
CARD = re.compile(r'<article class="consideration" id="([a-z0-9-]+)">.*?</article>', re.S)
BUTTON = re.compile(r'<p class="topic-discussion-link">.*?</p>', re.S)
RELATIVE = re.compile(r'((?:href|src)=")(\.\.?/[^"]*)')


def one_level_deeper(html):
    return RELATIVE.sub(lambda match: match[1] + '../' + match[2].removeprefix('./'), html)


def build():
    index = DOCS / 'considerations/index.html'
    html = index.read_text()
    head, remaining = html.split('<main id="content">', 1)
    _, foot = remaining.split('</main>', 1)
    form_url = re.search(r'href="(https://tally\.so/r/[^"]+)"',
                         (DOCS / 'participate/index.html').read_text())[1]
    canonical = re.search(r'<link rel="canonical" href="([^"]+)">', head)[1]
    topics = index.parent

    def render(match):
        slug = match[1]
        article = BUTTON.sub('', match[0])
        title = re.search(r'<h2>(.*?)</h2>', article)[1]
        page_head = one_level_deeper(head).replace('href="../" aria-current="page"', 'href="../"')
        page_head = page_head.replace(canonical, canonical + slug + '/')
        page_head = page_head.replace('What We’re Thinking About |', title + ' |')
        page_head = page_head.replace(
            'Conversation starters, developing ideas and thought experiments about AI governance.',
            'Read and respond to a Vocabulary Commons discussion topic.')
        body = one_level_deeper(article).replace('href="#', 'href="../#')
        body = body.replace('<h2>' + title + '</h2>',
                            '<h1>' + title + '</h1><p><a href="#comments">Join the discussion ↓</a></p>', 1)
        body = body.replace('<h3>', '<h2 class="topic-subheading">').replace('</h3>', '</h2>')
        comments = (
            '<section class="wrap prose section" id="comments"><h2>Join the discussion</h2>'
            '<p>What does this question miss? Share an example, a counterexample, or a different explanation.</p>'
            f'<p>Use <strong>{title}</strong> as the topic in your comment.</p>'
            f'<p><a class="button" href="{form_url}" rel="noreferrer noopener">Submit a comment</a></p>'
            '<p class="tiny-note">No GitHub account required. The Commons steward reviews submissions '
            'and may share them publicly if you give permission in the form.</p></section>'
        )
        topic = topics / slug / 'index.html'
        topic.parent.mkdir(exist_ok=True)
        topic.write_text(
            page_head + '<main id="content">'
            f'<p class="wrap"><a href="../#{slug}">← All discussion topics</a></p>'
            '<div class="wrap consideration-list">' + body + '</div>'
            + comments + '</main>' + one_level_deeper(foot))
        button = (
            f'<p class="topic-discussion-link"><a class="button secondary" href="{slug}/" '
            f'aria-label="Comment on {title}">Comment here</a></p>'
        )
        heading_end = article.index('</h2>') + len('</h2>')
        return article[:heading_end] + button + article[heading_end:]

    html, count = CARD.subn(render, html)
    if not count:
        raise ValueError('No discussion topics found on the Considerations page')
    index.write_text(html)
    return count


if __name__ == '__main__':
    print(f'Built {build()} topic discussion pages.')
