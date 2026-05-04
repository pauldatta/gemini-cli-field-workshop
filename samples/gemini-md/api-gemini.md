# Backend Layer Context

## Conventions
- All routes are defined in backend/routes/ and mounted in backend/server.js
- Use express.Router() — do not add routes directly to the app
- Middleware order: authMiddleware → checkObjectId → handler
- Error handling uses asyncHandler wrapper + custom errorMiddleware

## Error Handling
- Use the asyncHandler pattern from backend/middleware/asyncHandler.js
- Throw errors with appropriate HTTP status codes — the errorMiddleware catches them
- Never send raw error objects to the client — always use res.status(code).json({ message })
- Check for valid MongoDB ObjectIds using mongoose.Types.ObjectId.isValid() or the checkObjectId middleware

## Database
- Use Mongoose models defined in backend/models/
- Schema validation is handled at the Mongoose level
- Passwords are hashed using bcryptjs in the User model pre-save hook
- Never expose password fields in API responses — use .select('-password')

## Auth
- JWT tokens are stored in HTTP-only cookies, not localStorage
- Token verification is handled by authMiddleware in backend/middleware/authMiddleware.js
- Admin routes use the admin middleware check after authMiddleware
