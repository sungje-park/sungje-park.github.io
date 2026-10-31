# SP favicon

`sp-master.png` is the approved image generated with the built-in imagegen tool on 2026-10-29. The original PNG is preserved without alteration. It uses white SP initials on a charcoal rounded square with transparent corners.

`export.py` creates the five production icon files in `static/` using Pillow: 16px and 32px PNGs; an ICO containing 16, 32, 48, 64, 128, and 256px frames; an opaque 180px Apple touch icon; and a monochrome SVG traced from the approved white letter shapes for Safari pinned tabs. The SVG uses vector paths, not an embedded bitmap or a font dependency. Run `python3 assets/images/favicon/export.py` from any working directory to regenerate them.

## Original generation prompt

Use case: logo-brand. Asset type: preview of a personal academic website favicon. Create one square, minimalist, flat favicon: a solid charcoal rounded square in #1D1E20 with the exact white uppercase letters "SP" centered inside. Use a heavy, clean, modern sans-serif with simple open letterforms; the S and P must be distinct, side by side, with a modest clear gap and no overlapping or interlocking. Optically center the monogram, with generous consistent padding so the letters remain readable when reduced to 16 by 16 pixels. The charcoal square should occupy almost the entire square canvas, with moderately rounded corners. Only the pixels outside the rounded corners should be transparent. Straight-on flat vector-like graphic, crisp edges, exactly two colors plus transparent corner areas. No texture, no gradients, no shadows, no mockup, no border, no decorative elements, no extra text, no watermark. Output the single favicon on its own, not a presentation board.
