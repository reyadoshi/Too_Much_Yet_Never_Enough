import docx
import json
import os
import re

def parse_docx(docx_path):
    doc = docx.Document(docx_path)
    paragraphs = [p.text for p in doc.paragraphs]
    
    parts_def = [
        ("PART I", "The Girl Who Felt Everything", 1, 5),
        ("PART II", "People I Loved in Different Ways", 6, 10),
        ("PART III", "The Girl Who Kept Trying", 11, 18),
        ("PART IV", "Things I Never Said", 19, 24),
        ("PART V", "The Things I Couldn't Let Go Of", 25, 30),
        ("PART VI", "A Girl in the Mirror", 31, 35),
        ("PART VII", "The Little Things That Saved Me", 36, 42),
        ("PART VIII", "Too Much, Yet Never Enough", 43, 47),
        ("PART IX", "Letters I Never Meant to Send", 48, 53),
        ("PART X", "Enough", 54, 58),
    ]

    # Map paragraph index of each chapter header
    chap_header_regex = re.compile(r'^(\d+)\.\s*(.*)', re.IGNORECASE)
    
    # Store indices of headers
    items = [] # (index, type, label, title)
    
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i].strip()
        if p.startswith('PART '):
            part_num = p
            part_title = ''
            if i + 1 < len(paragraphs) and paragraphs[i+1].strip() and not paragraphs[i+1].strip().startswith('PART') and not chap_header_regex.match(paragraphs[i+1].strip()):
                part_title = paragraphs[i+1].strip()
                i += 1
            items.append((i, 'PART', part_num, part_title))
        elif chap_header_regex.match(p):
            m = chap_header_regex.match(p)
            ch_num_str = f"Chapter {m.group(1)}"
            ch_title_str = m.group(2).strip()
            items.append((i, 'CHAPTER', ch_num_str, ch_title_str))
        elif p == 'EPILOGUE' or p.startswith('EPILOGUE'):
            ep_title = ''
            if i + 1 < len(paragraphs) and paragraphs[i+1].strip():
                ep_title = paragraphs[i+1].strip()
                i += 1
            items.append((i, 'EPILOGUE', 'EPILOGUE', ep_title))
        i += 1

    print(f"Found {len(items)} structural markers.")

    book_data = {
        "title": "Too Much, Yet Never Enough",
        "author": "Zeyra",
        "parts": []
    }

    current_part = None
    
    for idx, item in enumerate(items):
        item_idx, item_type, label, title = item
        # Determine content end index
        next_idx = items[idx+1][0] if idx+1 < len(items) else len(paragraphs)
        
        if item_type == 'PART':
            # Create part object
            part_num_clean = label
            # Title from metadata list or manuscript
            current_part = {
                "id": f"part-{len(book_data['parts']) + 1}",
                "part_number": part_num_clean,
                "part_title": title,
                "chapters": []
            }
            book_data["parts"].append(current_part)
        elif item_type in ('CHAPTER', 'EPILOGUE'):
            # Extract content lines between item_idx + 1 and next_idx
            raw_lines = paragraphs[item_idx + 1 : next_idx]
            # Strip outer empty lines while preserving inner text lines
            content_lines = [line for line in raw_lines if line.strip()]
            
            # Form chapter dict
            if item_type == 'CHAPTER':
                ch_num_val = int(re.search(r'\d+', label).group())
                ch_obj = {
                    "id": f"ch-{ch_num_val}",
                    "chapter_number": label,
                    "title": title,
                    "full_title": f"{label}: {title}",
                    "content": content_lines
                }
            else: # EPILOGUE
                ch_obj = {
                    "id": "epilogue",
                    "chapter_number": "EPILOGUE",
                    "title": title,
                    "full_title": f"EPILOGUE: {title}" if title else "EPILOGUE",
                    "content": content_lines
                }
            
            if current_part is not None:
                ch_obj["part_id"] = current_part["id"]
                current_part["chapters"].append(ch_obj)
            else:
                # Fallback if chapter comes before any Part
                if not book_data["parts"]:
                    current_part = {
                        "id": "part-1",
                        "part_number": "PART I",
                        "part_title": "The Girl Who Felt Everything",
                        "chapters": []
                    }
                    book_data["parts"].append(current_part)
                ch_obj["part_id"] = current_part["id"]
                current_part["chapters"].append(ch_obj)

    return book_data

if __name__ == '__main__':
    data = parse_docx('Too_Much_Yet_Never_Enough_ORIGINAL.docx')
    
    total_chapters = sum(len(p['chapters']) for p in data['parts'])
    print(f"Total parts: {len(data['parts'])}, Total chapters: {total_chapters}")
    
    # Save parsed JSON to manuscript/parsed_manuscript.json and web/data/book.json
    with open('manuscript/parsed_manuscript.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open('web/data/book.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Saved parsed_manuscript.json and web/data/book.json successfully.")
