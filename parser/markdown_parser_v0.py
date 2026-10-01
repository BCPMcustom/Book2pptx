
import re, os
from parser.models.presentation_spec import (SlideSpec, PresentationSpec)
from html.parser import HTMLParser
import matplotlib.pyplot as plt

class TableParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.headers = []
        self.rows = []
        self.current_row = []
        self.current_cell = ""
        self.in_cell = False
        self.in_header = False


    def handle_starttag(self, tag, attrs):
        
        if tag in ("th", "td"):
            self.in_cell = True
            self.current_cell = ""
        elif tag == "tr":
            self.current_row = []

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

    def handle_endtag(self, tag):
        if tag in ("th", "td"):
            self.current_row.append(self.current_cell.strip())
            self.in_cell = False
        elif tag == "tr":
            if self.current_row:
                if self.in_header:
                    self.headers.append(self.current_row)
                else:
                    self.rows.append(self.current_row)


class HTMLTableRenderer:

    def __init__(self):
        self.table_count = 0

    def render(self, html_table):

        HEADER_LIMIT = 20
        CELL_LIMIT = 40
        total_width = 0
        column_widths = []
        display_rows = []
        parser = TableParser()
        parser.feed(html_table)
        rows = parser.rows

        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(current_dir, "..", "assets")
        filename = (f"table_{self.table_count}.png")
        output_path = os.path.normpath(os.path.join(assets_dir, filename))
        self.table_count += 1

        # Determine the number of columns
        num_columns = max(len(row) for row in rows)

        # Find the longest cell in each column

        for row_number, row in enumerate(rows):
            limit = HEADER_LIMIT if row_number == 0 else CELL_LIMIT
            display_row = []

            for cell in row:
                if len(cell) > limit:
                    cell = cell[:limit - 3] + "..."
                display_row.append(cell)
            display_rows.append(display_row)


        header = rows[0]
        data = rows[1:]

        for column in range(num_columns):
            header_length = len(header[column])
            data_length = max(len(row[column]) for row in data)      
            longest = max(len(row[column]) if column < len(row) else 0 for row in display_rows)
            column_widths.append(longest)
            
            # Matplotlib's table() does not properly account for header width
            # when calculating the rendered table geometry. When a header is
            # wider than the data in that column, reduce total_width to
            # compensate for Matplotlib's behavior.
            
            if header_length > data_length:
                total_width -= (header_length/data_length)   

        total_width += sum(column_widths)
        column_widths = [width / total_width for width in column_widths]


        fig, ax = plt.subplots()

        ax.axis("off")

        table = ax.table(
            cellText=rows[1:],
            colLabels=rows[0],
            loc="center",
            colWidths=column_widths
        )

        table.auto_set_font_size(False)
        table.set_fontsize(8)

        table.scale(1, 1.2)

        plt.savefig(
            output_path,
            bbox_inches="tight",
            dpi=200
        )

        plt.close(fig)

        return output_path

class MarkdownParser:

    def __init__(self):
        self.presentation_title = ""
        self.slides = []
        self.current_slide = None
        self.closing_title = ""
        self.table_renderer = HTMLTableRenderer()
        self.base_dir = ""


    def parse_heading(self, line):
        if line.startswith("# "):

            text = line[2:].strip()

            if self.presentation_title == "":
                self.presentation_title = text
            else:
                self.closing_title = text
            

        elif line.startswith("## "):
            title = line[3:].strip()
            print(f"NEW SLIDE: {title}")
            self.current_slide = SlideSpec(title)
            self.slides.append(self.current_slide)

    def parse_ignore(self, line, in_ignore):
        if line.startswith("### "):
            return True
        return in_ignore


        
    def parse_bullet(self, line):

        if line.startswith("- "):
            bullet = line[2:].strip()
            if self.current_slide:
                self.current_slide.bullets.append(bullet)


    def parse_image(self, line):

        IMAGE_RE = r'!\[(.*?)\]\((.*?)\)'

        match = re.search(IMAGE_RE, line)

        if match and self.current_slide is not None:
            filename = match.group(2)
            full_path = os.path.abspath(os.path.join(self.base_dir, filename))
            self.current_slide.images.append(full_path)


    def parse_callouts(self, line):

        if line.startswith("#### "):
            text = line[5:].strip()
            self.current_slide.callouts.append(text)


        
    def parse(self, filename):

        self.base_dir = os.path.dirname(filename)

        with open(filename, encoding="utf-8") as f:
            
            lines = f.readlines()
            
            table_lines = []
            in_ignore = False
            in_table = False
            
            i = 0

            while i < len(lines):

                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue

                if in_ignore:
                    if line.startswith("# ") or line.startswith("## ") or line.startswith("#### "):
                        in_ignore = False                    
                    elif line.startswith("### "):
                        in_ignore = False
                        i += 1
                        continue
                    else:
                        i += 1
                        continue

                if "<table" in line:                   
                    in_table = True
                    table_lines = [line]
                    i += 1
                    continue
                
                if in_table:
                    table_lines.append(line)
                    
                    if "</table>" in line:                        
                        html_table = "\n".join(table_lines)
                        image_filename = (self.table_renderer.render(html_table))
                        image_line = (f"![table]({image_filename})")
                        self.parse_image(image_line)
                        table_lines = []
                        in_table = False
                        i += 1
                        continue
                               
                self.parse_heading(line)
                self.parse_bullet(line)
                self.parse_image(line)
                self.parse_callouts(line)

                i += 1
                in_ignore = self.parse_ignore(line, in_ignore)

        return PresentationSpec(
            title=self.presentation_title,
            slides=self.slides,
            closing_title=self.closing_title
        )


