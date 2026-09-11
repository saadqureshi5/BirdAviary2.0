# Fix Breeding Pair Reactivation, Analytics Filtering, and Dashboard Count

Three bugs/missing features to address in the BirdAviary2.0 project.

---

## Issue 1: Breeding Pair — Add option to reactivate an ended pair

**Problem:** Once a breeding pair is ended (via the "End Pairing" button which sets `end_date`), there is no way to reactivate it. The "End Pairing" button is hidden when `end_date` is set, and no "Reactivate" button exists.

### Proposed Changes

#### [MODIFY] [BreedingRecordView.vue](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/views/breeding/BreedingRecordView.vue)
- Add a `reactivatePairing()` function that calls `breedingStore.updatePairing(id, { end_date: null })` after confirmation
- Add a "Reactivate Pairing" button that shows when `pairing.end_date` is set (the inverse condition of "End Pairing")
- Style it with a green/success color to contrast with the orange "End Pairing" button

#### [MODIFY] [PairingUpdate model in pairing.py](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/models/pairing.py)
- The `PairingUpdate` model already has `end_date: Optional[datetime] = None`, but the issue is that sending `end_date: null` from frontend may not properly clear the field because `model_dump(exclude_unset=True)` won't include a field explicitly set to `None` if it matches the default. We need to ensure that explicitly sending `end_date: null` is treated as "clear the end_date" rather than "not provided".
- Update the `update_pairing` service to handle `end_date` being explicitly set to `None` (reactivation case)

#### [MODIFY] [breeding_service.py](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/services/breeding_service.py)
- Update `update_pairing()` to properly handle `end_date` being explicitly set to `None` vs not being provided at all. Use the request body directly or adjust the exclude logic.

---

## Issue 2: Breeding Analytics — Filter by category

**Problem:** The Breeding Analytics page (`BreedingAnalyticsView.vue`) shows global stats across ALL categories. There is no category filter dropdown, unlike the Pairs Overview page which already has one. Users want to see breeding performance broken down by category.

### Proposed Changes

#### [MODIFY] [BreedingAnalyticsView.vue](file:///c:/Users/saadq/Desktop/BirdAviary2.0/src/views/breeding/BreedingAnalyticsView.vue)
- Import `useBirdsStore` and fetch categories on mount
- Add a `selectedCategory` ref and category filter dropdown in the header area
- When a category is selected, pass it as a query parameter to the analytics API: `GET /breeding/analytics?category_id=X`
- Recompute displayed stats based on filtered analytics response

#### [MODIFY] [breeding_service.py](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/services/breeding_service.py)
- Update `get_breeding_analytics()` to accept an optional `category_id` parameter
- When `category_id` is provided, filter pairings to only those where `bird_a` or `bird_b` belongs to that category
- Filter clutches and chicks accordingly so all stats reflect only the selected category

#### [MODIFY] [breeding.py router](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/routers/breeding.py)
- Add `category_id: Optional[int] = None` query parameter to the `/analytics` endpoint
- Pass it through to `breeding_service.get_breeding_analytics(session, category_id)`

---

## Issue 3: Wrong conure category count on dashboard

**Problem:** The dashboard's "Category Breakdown" section shows incorrect bird counts for the Conure category. The root cause is that the `GET /categories` endpoint in [categories.py](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/routers/categories.py) counts ALL birds in each category regardless of status (including `external` birds), while the dashboard stats exclude `external` birds.

Birds with status `external` are used as references (e.g., for parentage tracking of birds acquired from outside) and should NOT be counted in the dashboard's category breakdown.

### Proposed Changes

#### [MODIFY] [categories.py router](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/routers/categories.py)
- Update the `bird_count` calculation in `get_categories()` to exclude birds with status `'external'`:
  ```python
  count = len(session.exec(select(Bird).where(Bird.category_id == cat.id, Bird.status != 'external')).all())
  ```

#### [MODIFY] [bird_service.py](file:///c:/Users/saadq/Desktop/BirdAviary2.0/backend/services/bird_service.py)
- Similarly update `get_bird_count_by_category()` to exclude `'external'` birds for consistency:
  ```python
  count = len(session.exec(select(Bird).where(Bird.category_id == cat.id, Bird.status != 'external')).all())
  ```

---

## Verification Plan

### Manual Verification
1. **Reactivation:** End a pairing → verify "Reactivate" button appears → click it → verify pair becomes Active again with `end_date` cleared
2. **Analytics filtering:** Open Breeding Analytics → select a category → verify stats update to reflect only pairs in that category
3. **Dashboard count:** Check Category Breakdown section → verify Conure count matches the actual number of non-external birds in that category
