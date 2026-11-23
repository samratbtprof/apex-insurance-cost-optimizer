# Page 1 "Leakage overview": click-by-click steps

Menu names vary a little between APEX versions (23.x, 24.x). If a label differs, look for the nearest one and tell me what you see. The SQL for each region is in `docs/apex-build-guide.md` (Part 3).

## A. Create the application and rename page 1
1. App Builder, Create, New Application.
2. Name: `Insurance Cost Optimizer`. Leave the default features. Click Create Application.
3. Open the application, then open page 1 (Home) in Page Designer.
4. Click the page name at the top of the left tree (Page 1). In the Property Editor on the right, set Name to `Leakage overview` and Title to `Leakage overview`. Click Save.

## B. How to add a region in Page Designer (used four times)
1. In the left pane, Rendering tab, find the tree: Page, Regions, Content Body.
2. Right-click Content Body, then Create Region. (Or open the Gallery at the bottom and drag a region type onto Content Body.)
3. Select the new region. In the Property Editor set Title and Type, then Source, then Layout.
4. Click Save, then Run (the play button, top right) to look at the page. Come back with the Edit Page link at the bottom of the running page.

## C. Region A: KPI cards
1. Create a region. Title: `Key figures`. Type: `Cards`.
2. Source: Location `Local Database`, Type `SQL Query`. Paste the KPI SQL from the build guide (Region A).
3. Select the Attributes node under the region (below the region in the tree). Set:
   - Layout: Grid, columns: 4.
   - Card, Title, Column: `VALUE`.
   - Card, Subtitle, Column: `TITLE`.
4. Layout: Start New Row on, Column Span 12.
5. Save, Run. You should see four cards: the claimed total, the leakage total, 16.0% and 3,224.

## D. Region B: leakage by cause
1. Create a region. Title: `Leakage by cause`. Type: `Chart`.
2. In the tree, the region now has a Chart child (Attributes) and a Series child (New). Select Attributes. Set Type `Bar`, Orientation `Horizontal`.
3. Select the Series (New). Set Name `Leakage`. Source: Location `Local Database`, Type `SQL Query`. Paste the SQL from the build guide (Region B).
4. Column Mapping: Label `LABEL`, Value `VALUE`.
5. Layout: Start New Row on, Column Span 6.
6. Save, Run. You should see four bars: OFF_FORMULARY, GENERIC_MISSED, REIMBURSEMENT_LOSS, OVER_DISPENSE, in that size order.

## E. Region C: leakage by month, stacked
1. Create a region. Title: `Leakage by month`. Type: `Chart`.
2. Select Attributes. Set Type `Bar` (vertical), and turn Stack on.
3. Select the Series. Source: SQL Query, paste the SQL from the build guide (Region C).
4. Column Mapping: Series Name `SERIES_NAME`, Label `MONTH_LABEL`, Value `VALUE`. Because the query gives one row per month and cause, setting Series Name makes one stacked colour per cause.
5. Layout: Start New Row off (it sits beside region B), Column Span 6.
6. Save, Run. You should see 14 bars, 2025-01 to 2026-02 (the synthetic claims span 14 months), each split into four colours.

## F. Region D: leakage by provider
1. Create a region. Title: `Leakage by provider`. Type: `Chart`.
2. Attributes: Type `Bar`, Orientation `Horizontal`.
3. Series: Source SQL Query, paste the SQL from the build guide (Region D). Column Mapping: Label `LABEL`, Value `VALUE`.
4. Layout: Start New Row on, Column Span 12.
5. Save, Run. Expected bars, largest first: Synthetic General Hospital 746,891; Synthetic Metro Hospital 695,129; Synthetic Care Pharmacy 463,487; Synthetic City Clinic 335,778; Synthetic Community Clinic 254,737.

## G. A note that the data is synthetic (optional but recommended)
1. Create a region. Title: `About this data`. Type: `Static Content`.
2. Source, Text: `Synthetic data. Reference implementation. Not client data.`
3. Layout: Start New Row on, Column Span 12. Move it to the bottom.

## H. Rupee sign and number format (optional)
In a chart, look under the Series or the Value axis for a number format or prefix setting, and set the prefix to the rupee sign. If you cannot find it, skip it. The values are correct without it.

## If something goes wrong
- A chart is empty: open the region Source and press the validate button. If the query is valid, check that the column names in Column Mapping match the SQL aliases exactly (they are upper case: `LABEL`, `VALUE`, `MONTH_LABEL`, `SERIES_NAME`).
- A region shows an error: copy the full text and send it to me.
- Send me a screenshot of the running page and of Page Designer if the layout is wrong.
