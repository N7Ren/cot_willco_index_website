import json
import os
from datetime import datetime, timezone
from collections import defaultdict

def get_color_span(val, val_type):
    if val_type == "index":
        if val <= 10:
            return f'<span class="text-red">{int(round(val))}</span>'
        elif val >= 90:
            return f'<span class="text-green">{int(round(val))}</span>'
        else:
            return f'{int(round(val))}'
    return str(val)

def get_unique_asset_count(data):
    return len(set(d.get('market_and_exchange_names') for d in data))

def format_years(val):
    val_float = float(val)
    return str(int(val_float) if val_float.is_integer() else val)

def generate_markdown_table(data, cols):
    # cols is a list of dicts: {'id': '', 'label': '', 'type': ''}
    header_labels = [c['label'] for c in cols]
    header_line = "| " + " | ".join(header_labels) + " |"
    sep_line = "|" + "|".join([":---:"] * len(cols)) + "|"
    
    rows = []
    for row in data:
        row_cells = []
        for c in cols:
            val = None
            if c['id'] == 'combined_speculators':
                val = 100 - row['willco_commercials_index']
            else:
                val = row.get(c['id'])
                
            if c['id'] == 'lookback_(y)':
                val_float = float(val)
                row_cells.append(str(int(val_float) if val_float.is_integer() else val))
            elif c.get('type') == 'index':
                # Use our formatting
                row_cells.append(get_color_span(val, 'index'))
            else:
                row_cells.append(str(val))
        rows.append("| " + " | ".join(row_cells) + " |")
        
    return "\n".join([header_line, sep_line] + rows) + "\n{: .table .table-sm .table-hover .screener-table .w-100 }"


def generate_grouped_html(data, section_type):
    # section_type can be 'combined' or 'separated'
    # Group data by asset
    grouped = defaultdict(list)
    for row in data:
        name = row['market_and_exchange_names']
        grouped[name].append(row)
        
    html_parts = []
    
    for asset, rows in sorted(grouped.items()):
        html_parts.append('<div class="blog-asset-card">')
        html_parts.append(f'<div class="asset-card-header">{asset}</div>')
        html_parts.append('<div class="asset-table-wrapper">')
        html_parts.append('<table class="blog-compact-table">')
        
        if section_type == 'combined':
            html_parts.append('<thead><tr><th>Yrs</th><th>Comm</th><th>Specs</th></tr></thead>')
            html_parts.append('<tbody>')
            for row in rows:
                yrs = format_years(row.get('lookback_(y)', 0))
                comm = get_color_span(row['willco_commercials_index'], 'index')
                spec_val = 100 - row['willco_commercials_index']
                spec = get_color_span(spec_val, 'index')
                
                html_parts.append(f'<tr><td>{yrs}</td><td>{comm}</td><td>{spec}</td></tr>')
            html_parts.append('</tbody>')
            
        else:
            html_parts.append('<thead><tr><th>Yrs</th><th>Comm</th><th>Specs<br><small>(Large / Small)</small></th></tr></thead>')
            html_parts.append('<tbody>')
            for row in rows:
                yrs = format_years(row.get('lookback_(y)', 0))
                comm = get_color_span(row['willco_commercials_index'], 'index')
                large = get_color_span(row['willco_large_specs_index'], 'index')
                small = get_color_span(row['willco_small_specs_index'], 'index')
                
                html_parts.append(f'<tr><td>{yrs}</td><td>{comm}</td><td>L: {large} / S: {small}</td></tr>')
            html_parts.append('</tbody>')

        html_parts.append('</table>')
        html_parts.append('</div>')
        html_parts.append('</div>')
        
    return "\n".join(html_parts)

def main():
    data_path = os.path.join(os.path.dirname(__file__), '../_data/data.json')
    if not os.path.exists(data_path):
        print("data.json not found")
        return
        
    with open(data_path, 'r') as f:
        json_data = json.load(f)
        
    all_data = json_data.get('data', [])
    years = 5.0
    low = 10
    high = 90
    
    # Filter years
    filtered = []
    for row in all_data:
        try:
            if float(row.get('lookback_(y)', 0)) <= years:
                filtered.append(row)
        except ValueError:
            pass
            
    # Sort by market alphabetically
    filtered.sort(key=lambda x: x.get('market_and_exchange_names', ''))
    
    # Combined
    combined_data = []
    for row in filtered:
        combined = 100 - row['willco_commercials_index']
        # The client condition: ((row.willco_commercials_index >= high && combined <= low) || (row.willco_commercials_index <= low && combined >= high))
        if (row['willco_commercials_index'] >= high and combined <= low) or \
           (row['willco_commercials_index'] <= low and combined >= high):
            combined_data.append(row)
            
    cols_combined = [
        {"id": "market_and_exchange_names", "label": "Market"},
        {"id": "lookback_(y)", "label": "Years"},
        {"id": "willco_commercials_index", "label": "Commercials", "type": "index"},
        {"id": "combined_speculators", "label": "Speculators", "type": "index"}
    ]
    
    # Separated Strict
    sep_strict_data = []
    for row in filtered:
        c = row['willco_commercials_index']
        l = row['willco_large_specs_index']
        s = row['willco_small_specs_index']
        if (c >= high and l <= low and s <= low) or \
           (c <= low and l >= high and s >= high):
            sep_strict_data.append(row)
            
    cols_separated = [
        {"id": "market_and_exchange_names", "label": "Market"},
        {"id": "lookback_(y)", "label": "Years"},
        {"id": "willco_commercials_index", "label": "Commercials", "type": "index"},
        {"id": "willco_large_specs_index", "label": "Large Speculators", "type": "index"},
        {"id": "willco_small_specs_index", "label": "Small Speculators", "type": "index"}
    ]
            
    # Separated Loose
    sep_loose_data = []
    for row in filtered:
        c = row['willco_commercials_index']
        l = row['willco_large_specs_index']
        s = row['willco_small_specs_index']
        if c >= high or c <= low or l >= high or l <= low or s >= high or s <= low:
            sep_loose_data.append(row)
            
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    position_date = all_data[0].get('as_of_date_in_form_yyyy_mm_dd', 'N/A') if all_data else "N/A"
    post_filename = f"{date_str}-Potential-Setups.md"
    post_path = os.path.join(os.path.dirname(__file__), '../_posts', post_filename)
    
    with open(post_path, 'w') as f:
        f.write(f"---\n")
        f.write(f"layout: post\n")
        f.write(f"title: \"{date_str} Potential Setups\"\n")
        f.write(f"date: {date_str}\n")
        f.write(f"position_date: \"{position_date}\"\n")
        f.write(f"show_methodology: true\n")
        f.write(f"---\n\n")
        
        resources_text = "If you want to learn more about how to apply this data in your trading see [Resources]({{ '/resources/' | relative_url }})\n\n"
        
        def write_section(title, section_data, section_type, cols):
            f.write(f"<details markdown=\"1\">\n")
            f.write(f"<summary><h2 id=\"speculators-{section_type}\">{title} ({get_unique_asset_count(section_data)} assets)</h2></summary>\n\n")
            f.write(resources_text)
            if section_data:
                # Desktop view
                f.write("<div class=\"d-none d-md-block\" markdown=\"1\">\n\n")
                f.write(generate_markdown_table(section_data, cols) + "\n\n")
                f.write("</div>\n")
                # Mobile view
                f.write("<div class=\"d-block d-md-none\">\n\n")
                f.write(generate_grouped_html(section_data, 'combined' if 'combined' in title else 'separated') + "\n\n")
                f.write("</div>\n\n")
            else:
                f.write("No setups found.\n\n")
            f.write(resources_text)
            f.write("</details>\n")
            
        write_section("Speculators combined", combined_data, "combined", cols_combined)
        write_section("Speculators separated (strict)", sep_strict_data, "separated-strict", cols_separated)
        write_section("Speculators separated (loose)", sep_loose_data, "separated-loose", cols_separated)
            
    print(f"Generated {post_filename}")

if __name__ == '__main__':
    main()
