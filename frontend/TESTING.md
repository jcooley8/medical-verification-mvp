# Testing the Click-to-Verify Frontend

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   Navigate to http://localhost:5173

## Testing Without a PDF

The application will load with mock data even without a PDF file. You can:
- View the Medical Chronology and Billing tabs
- See the mock extraction data displayed in cards/rows
- Click "Verify" buttons (they won't highlight since there's no PDF, but you can see the UI interaction)

## Testing With a Sample PDF

To fully test the click-to-verify feature:

1. **Add a sample PDF:**
   - Place a PDF file in `public/sample-medical-record.pdf`
   - Or update `src/data/mockData.ts` to point to your PDF URL

2. **Verify the bounding boxes:**
   - The mock data includes bounding box coordinates
   - When you click "Verify" on any data item, the PDF should:
     - Jump to the correct page
     - Show a yellow highlight box
     - Display confidence percentage badge

3. **Test cases to verify:**
   - [ ] Click verify on a chronology event → highlights date field on page 1
   - [ ] Click verify on another event → highlights switch to page 3
   - [ ] Click verify on billing item → jumps to page 7
   - [ ] Zoom in/out → highlights scale correctly
   - [ ] Switch tabs → clears previous highlights
   - [ ] Click on highlighted area → dismisses highlight

## Mock Data Structure

The mock data includes:
- **3 chronology events** with source references on pages 1, 3, and 5
- **3 bill line items** with source references on page 7
- **Confidence scores** ranging from 78% to 99% to test different visual indicators

## Customizing Mock Data

Edit `src/data/mockData.ts` to:
- Change the PDF URL
- Adjust bounding box coordinates to match your test PDF
- Add more events or billing items
- Test different confidence levels

## Backend Integration

To connect to the real backend:

1. Update `src/App.tsx` to fetch from API instead of using mock data:
   ```typescript
   const { data: extraction } = useQuery({
     queryKey: ['extraction', documentId],
     queryFn: () => fetch(`/api/v1/documents/${documentId}`).then(r => r.json())
   });
   ```

2. Install TanStack Query provider in `src/main.tsx`

3. Point to your backend API endpoint

## Known Limitations (MVP)

- No file upload UI (using hardcoded mock data)
- No error boundaries
- Highlights may not perfectly align if PDF has unusual rotation/scaling
- No responsive mobile layout yet
