# Backend Context — Express.js API

## Conventions
- Every route file exports a router and uses `express.Router()`
- Controllers are the only place for business logic
- Use `asyncHandler` wrapper from `backend/middleware/asyncHandler.js` for all async route handlers
- Validate all request body fields before processing
- Return proper HTTP status codes: 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 404 (not found)

## Error Handling
- All errors go through `backend/middleware/errorMiddleware.js`
- Never catch errors silently — let them propagate to the error middleware
- Include meaningful error messages: `res.status(404); throw new Error('Product not found');`

## Database
- Models use Mongoose schemas in `backend/models/`
- Always use `.lean()` for read-only queries (performance)
- Index frequently queried fields
- Use transactions for multi-document operations

## Security
- JWT tokens stored in HTTP-only cookies — never in localStorage
- Validate MongoDB ObjectIds with `checkObjectId` middleware before database queries
- Sanitize user inputs to prevent injection attacks
- Rate limit authentication endpoints
