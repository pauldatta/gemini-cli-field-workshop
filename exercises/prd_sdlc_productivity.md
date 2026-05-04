# PRD: Product Wishlist Feature

> **Workshop Use:** Practice exercise for Use Case 1 (SDLC Productivity Enhancement). Exercises the full SDLC workflow: context engineering → Conductor planning → implementation → governance → review.

## Problem

Users browsing the ProShop storefront have no way to save products for later. They must either add items directly to their cart (creating purchase pressure) or remember products manually. This results in lower return visits and missed conversion opportunities.

## Users

| Role | Need |
|---|---|
| **Shopper** | Save products I'm interested in without committing to purchase. Come back later and find them easily. |
| **Returning User** | See my saved items across sessions. Move items from wishlist to cart when ready to buy. |
| **Guest User** | Understand that wishlist requires an account. Get prompted to sign up/log in when trying to save. |

## Features

### 1. Wishlist Data Model
- Add a `wishlist` field to the User model: array of ObjectId references to Products
- Maximum 50 items per wishlist (prevent abuse)
- Timestamps for when each item was added (for sorting)
- No duplicate products in the same wishlist

### 2. Wishlist API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users/wishlist` | Get current user's wishlist with populated product details |
| `POST` | `/api/users/wishlist/:productId` | Add a product to the wishlist |
| `DELETE` | `/api/users/wishlist/:productId` | Remove a product from the wishlist |
| `POST` | `/api/users/wishlist/:productId/to-cart` | Move a product from wishlist to cart |

All endpoints require authentication (JWT).

### 3. Frontend Components

| Component | Description |
|---|---|
| **WishlistButton** | Heart icon on ProductCard and ProductScreen. Filled = in wishlist, outline = not. Toggle on click. |
| **WishlistScreen** | Full page listing wishlist items as ProductCards. "Remove" and "Move to Cart" actions per item. |
| **WishlistBadge** | Small count badge in the header navigation showing total wishlist items. |
| **AuthPrompt** | Modal shown to unauthenticated users who click the wishlist button. "Log in to save items." |

### 4. State Management
- Create `wishlistApiSlice.js` using RTK Query
- Endpoints: `getWishlist`, `addToWishlist`, `removeFromWishlist`, `moveToCart`
- Optimistic updates on add/remove for responsive UI
- Cache invalidation on mutations

## Technical Constraints

- Follow existing ProShop patterns: asyncHandler, errorMiddleware, checkObjectId
- Use the same JWT auth middleware as other protected routes
- No new database collections — extend the existing User model
- Frontend must match existing ProShop styling (React-Bootstrap)
- Write tests for all API endpoints: happy path, auth failures, duplicate prevention, max limit

## Workshop Integration

This PRD is designed to exercise the following Gemini CLI features:

1. **GEMINI.md context**: The agent should follow the project's coding conventions (async/await, controller pattern, error middleware)
2. **Conductor**: Plan the implementation as a multi-phase track:
   - Phase 1: Data model changes
   - Phase 2: API endpoints + tests
   - Phase 3: Frontend components
   - Phase 4: Integration + E2E testing
3. **Subagents**: Delegate security review to `@security-scanner`
4. **Policy engine**: The policy should block any hardcoded auth tokens in the implementation
5. **Hooks**: The secret-scanner hook should catch any hardcoded credentials; the test-nudge hook should remind the agent to run tests after each phase

## Success Criteria

- [ ] Wishlist persists across sessions (stored in MongoDB, not localStorage)
- [ ] Heart icon toggles correctly on product cards and product detail page
- [ ] "Move to Cart" removes from wishlist and adds to cart in one action
- [ ] Guest users see login prompt, not an error
- [ ] All 4 API endpoints have test coverage (happy path + error cases)
- [ ] No hardcoded credentials or secrets in the implementation
- [ ] Implementation follows the GEMINI.md conventions (controller pattern, asyncHandler, etc.)
