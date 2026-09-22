import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import json
import os
import shutil

def add_page_number(run):
    """Add dynamic page number field to a run in python-docx."""
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_book_docx(json_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        book = json.load(f)

    doc = docx.Document()

    # Define standard margins (1 inch top/bottom, 0.8 inch left/right)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(6.0)  # Standard 6x9 book dimensions
        section.page_height = Inches(9.0)

    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Georgia'
    normal_font.size = Pt(10.5)
    normal_font.color.rgb = RGBColor(0x2C, 0x28, 0x25) # Warm charcoal

    # --- 1. COVER PAGE ---
    if os.path.exists('Cover.png'):
        p_cov = doc.add_paragraph()
        p_cov.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cov.paragraph_format.space_before = Pt(0)
        p_cov.paragraph_format.space_after = Pt(0)
        run_cov = p_cov.add_run()
        run_cov.add_picture('Cover.png', width=Inches(5.0))
        doc.add_page_break()

    # --- 2. TITLE PAGE WITH SIGNATURE ---
    p_title_top = doc.add_paragraph()
    p_title_top.paragraph_format.space_before = Pt(80)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run(book['title'].upper())
    run_title.font.name = 'Georgia'
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1F, 0x1B, 0x18)
    p_title.paragraph_format.space_after = Pt(16)

    # Decorative Line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_line = p_line.add_run("― ― ―")
    run_line.font.name = 'Georgia'
    run_line.font.size = Pt(12)
    run_line.font.color.rgb = RGBColor(0x8C, 0x7B, 0x6B)
    p_line.paragraph_format.space_after = Pt(20)

    # Author
    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_author = p_author.add_run(f"by  {book['author']}")
    run_author.font.name = 'Georgia'
    run_author.font.size = Pt(13)
    run_author.font.italic = True
    run_author.font.color.rgb = RGBColor(0x5A, 0x52, 0x4C)
    p_author.paragraph_format.space_after = Pt(18)

    # Author Signature
    if os.path.exists('Signature.png'):
        p_sig = doc.add_paragraph()
        p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sig = p_sig.add_run()
        run_sig.add_picture('Signature.png', width=Inches(2.2))

    doc.add_page_break()

    # --- 3. TABLE OF CONTENTS PAGE ---
    p_toc_head = doc.add_paragraph()
    p_toc_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_toc_head = p_toc_head.add_run("CONTENTS")
    run_toc_head.font.name = 'Georgia'
    run_toc_head.font.size = Pt(16)
    run_toc_head.font.bold = True
    run_toc_head.font.color.rgb = RGBColor(0x1F, 0x1B, 0x18)
    p_toc_head.paragraph_format.space_before = Pt(36)
    p_toc_head.paragraph_format.space_after = Pt(24)

    for part in book['parts']:
        p_toc_part = doc.add_paragraph()
        run_tp = p_toc_part.add_run(f"{part['part_number']} ― {part['part_title'].upper()}")
        run_tp.font.name = 'Georgia'
        run_tp.font.size = Pt(10)
        run_tp.font.bold = True
        run_tp.font.color.rgb = RGBColor(0x4A, 0x3F, 0x35)
        p_toc_part.paragraph_format.space_before = Pt(12)
        p_toc_part.paragraph_format.space_after = Pt(4)

        for ch in part['chapters']:
            p_toc_ch = doc.add_paragraph()
            p_toc_ch.paragraph_format.left_indent = Inches(0.25)
            p_toc_ch.paragraph_format.space_after = Pt(2)
            run_tc = p_toc_ch.add_run(ch['full_title'])
            run_tc.font.name = 'Georgia'
            run_tc.font.size = Pt(9.5)
            run_tc.font.color.rgb = RGBColor(0x5C, 0x54, 0x4D)

    doc.add_page_break()

    # Setup Section Header / Footer for Body
    body_section = doc.sections[-1]
    footer = body_section.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f_run = f_p.add_run()
    f_run.font.name = 'Georgia'
    f_run.font.size = Pt(9)
    f_run.font.color.rgb = RGBColor(0x8C, 0x7B, 0x6B)
    add_page_number(f_run)

    # --- 4. BODY CONTENT ---
    for part in book['parts']:
        # Part Start Page
        p_part_top = doc.add_paragraph()
        p_part_top.paragraph_format.space_before = Pt(120)

        p_part_num = doc.add_paragraph()
        p_part_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_pn = p_part_num.add_run(part['part_number'].upper())
        run_pn.font.name = 'Georgia'
        run_pn.font.size = Pt(12)
        run_pn.font.bold = True
        run_pn.font.color.rgb = RGBColor(0x8C, 0x7B, 0x6B)
        p_part_num.paragraph_format.space_after = Pt(12)

        p_part_title = doc.add_paragraph()
        p_part_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_pt = p_part_title.add_run(part['part_title'])
        run_pt.font.name = 'Georgia'
        run_pt.font.size = Pt(20)
        run_pt.font.bold = True
        run_pt.font.color.rgb = RGBColor(0x1F, 0x1B, 0x18)
        p_part_title.paragraph_format.space_after = Pt(48)

        # Page Break after Part Title Page
        doc.add_page_break()

        # Chapters in Part
        for ch_idx, ch in enumerate(part['chapters']):
            if ch_idx > 0:
                p_gap = doc.add_paragraph()
                p_gap.paragraph_format.space_before = Pt(36)

            # Chapter Title Header
            p_ch_hdr = doc.add_paragraph()
            p_ch_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_ch_hdr.paragraph_format.space_before = Pt(24)
            p_ch_hdr.paragraph_format.space_after = Pt(14)
            p_ch_hdr.paragraph_format.keep_with_next = True

            run_chn = p_ch_hdr.add_run(f"{ch['chapter_number']}\n" if ch['chapter_number'] != 'EPILOGUE' else "EPILOGUE\n")
            run_chn.font.name = 'Georgia'
            run_chn.font.size = Pt(10)
            run_chn.font.bold = True
            run_chn.font.color.rgb = RGBColor(0x8C, 0x7B, 0x6B)

            run_cht = p_ch_hdr.add_run(ch['title'])
            run_cht.font.name = 'Georgia'
            run_cht.font.size = Pt(15)
            run_cht.font.bold = True
            run_cht.font.color.rgb = RGBColor(0x1F, 0x1B, 0x18)

            # Chapter Paragraph Content
            for line in ch['content']:
                p_body = doc.add_paragraph()
                p_body.paragraph_format.space_before = Pt(0)
                p_body.paragraph_format.space_after = Pt(6)
                p_body.paragraph_format.line_spacing = 1.25

                run_b = p_body.add_run(line)
                run_b.font.name = 'Georgia'
                run_b.font.size = Pt(10.5)
                run_b.font.color.rgb = RGBColor(0x2C, 0x28, 0x25)

            # Signature at the end of Epilogue
            if ch['id'] == 'epilogue' and os.path.exists('Signature.png'):
                p_ep_sig_gap = doc.add_paragraph()
                p_ep_sig_gap.paragraph_format.space_before = Pt(24)
                p_ep_sig = doc.add_paragraph()
                p_ep_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_esig = p_ep_sig.add_run()
                run_esig.add_picture('Signature.png', width=Inches(2.0))

    # --- 5. BACK COVER PAGE ---
    if os.path.exists('Back_Cover.png'):
        doc.add_page_break()
        p_bcov = doc.add_paragraph()
        p_bcov.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_bcov.paragraph_format.space_before = Pt(0)
        p_bcov.paragraph_format.space_after = Pt(0)
        run_bcov = p_bcov.add_run()
        run_bcov.add_picture('Back_Cover.png', width=Inches(5.0))

    doc.save(output_path)
    print(f"Successfully generated DOCX with Cover, Signature, and Back Cover at {output_path}")

if __name__ == '__main__':
    json_file = 'manuscript/parsed_manuscript.json'
    doc_out = 'document/Too_Much_Yet_Never_Enough_Zeyra.docx'
    root_doc_out = 'Too_Much_Yet_Never_Enough_Zeyra.docx'

    create_book_docx(json_file, doc_out)
    shutil.copyfile(doc_out, root_doc_out)
    print(f"Copied DOCX to root workspace: {root_doc_out}")
