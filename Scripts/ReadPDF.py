import glob

from tika import parser
from pdfreader import SimplePDFViewer, PageDoesNotExist


def tika(filename):
    raw_text = parser.from_file(filename, xmlContent=True)
    lines = []
    page = ''

    for line in raw_text['content'].split('\n'):
        if line.startswith('<div'):
            page = ''
        elif line.startswith('</div'):
            lines.append(page.split('</p>')[0])
        elif line.startswith('<p>'):
            page += f'{line.split("<p>")[1]}\n'

    return lines


def pdfread(filename):
    fd = open(filename, "rb")
    viewer = SimplePDFViewer(fd)

    pdf_markdown = []

    try:
        while True:
            viewer.render()
            pdf_markdown.append(viewer.canvas.strings)
            viewer.next()
    except PageDoesNotExist:
        pass

    return pdf_markdown


def main():
    file = glob.glob('./../Patient_data/*.pdf')[0]
    words = pdfread(file)
    lines = tika(file)

    pages = []
    rows = []
    row = []

    for word, line in zip(words, lines):
        from_to = 0
        line = line.split('\n')

        for i in range(len(line)):
            for wor in word[from_to:]:
                if wor in line[i] and wor not in row:
                    from_to += 1
                    row.append(wor)
                else:
                    break

            rows.append(row)
            row = []

        pages.append(rows)
        row = []
        rows = []

    if len(pages[0][1]) != len(pages[0][2]):
        if '+' not in pages[0][2][5] and '-' not in pages[0][2][5]:
            pages[0][2].insert(5, '-')
        if len(pages[0][2][6].split('/')) != 2:
            pages[0][2].insert(6, '-')

    with open('./../temp/health_data.csv', 'w') as file:
        for p in pages:
            for r in p:
                file.write(f"{','.join(r)}\n")
            file.write('\n')


if __name__ == '__main__':
    main()
