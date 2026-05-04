# Project: ProShop eCommerce (Workshop Demo)

## Stack
- Backend: Express.js with MongoDB/Mongoose (backend/)
- Frontend: React with Redux Toolkit & RTK Query (frontend/)
- Auth: JWT with HTTP-only cookies
- File uploads: Multer
- Package manager: npm

## Architecture
- Routes in backend/routes/ — register middleware, delegate to controllers
- Business logic in backend/controllers/ — never in route files
- Data models in backend/models/ — Mongoose schemas
- Frontend state via RTK Query slices in frontend/src/slices/

## Rules
- Use async/await — never raw callbacks
- Follow the asyncHandler pattern in backend/middleware/
- Error responses must go through the custom errorMiddleware
- All route params that are MongoDB ObjectIds must use checkObjectId middleware
- New endpoints must include proper error handling for invalid IDs and missing resources
