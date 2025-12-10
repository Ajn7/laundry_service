# Laundry Service API Documentation (Vendor Edition)

## Base URL
```
http://your-domain.com/api/
```

---

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [Vendor APIs](#vendor-apis)
3. [Laundry Service APIs](#laundry-service-apis)
4. [Address Search API](#address-search-api)
5. [Service Type APIs](#service-type-apis)
6. [Service Offering APIs](#service-offering-apis)
7. [Operating Hours APIs](#operating-hours-apis)
8. [Review APIs](#review-apis)
9. [Booking APIs](#booking-apis)

---

## Authentication APIs

### 1. Send OTP (Customer Registration)
**Endpoint:** `/api/auth/send-otp/`  
**Method:** `POST`  
**Authentication:** Not Required  
**Description:** Request to send OTP to email or phone number for customer registration

**Request Body:**
```json
{
  "email": "user@example.com",
  "user_type": "customer"
}
```
OR
```json
{
  "country_code": "+91",
  "phone_number": "9876543210",
  "user_type": "customer"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "OTP sent successfully",
  "otp": "123456"  // Only in DEBUG mode
}
```

---

### 2. Send OTP (Vendor Registration)
**Endpoint:** `/api/auth/send-otp/`  
**Method:** `POST`  
**Authentication:** Not Required  
**Description:** Request to send OTP to email or phone number for vendor registration

**Request Body:**
```json
{
  "email": "vendor@example.com",
  "user_type": "vendor"
}
```
OR
```json
{
  "country_code": "+91",
  "phone_number": "9876543210",
  "user_type": "vendor"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "OTP sent successfully",
  "otp": "123456"  // Only in DEBUG mode
}
```

---

### 3. Verify OTP (Customer Login)
**Endpoint:** `/api/auth/verify-otp/`  
**Method:** `POST`  
**Authentication:** Not Required  
**Description:** Verify OTP and get authentication token for customer

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "user_type": "customer"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "user_exists": true,
  "token": "a1b2c3d4e5f6g7h8i9j0...",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "country_code": "+91",
    "phone_number": "9876543210",
    "full_phone": "+919876543210",
    "user_type": "customer",
    "is_verified": true,
    "is_active": true,
    "is_staff": false,
    "created_at": "2023-12-10T10:30:00Z",
    "updated_at": "2023-12-10T10:30:00Z"
  },
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "pincode": "560001",
    "address": "123 Main St",
    "created_at": "2023-12-10T10:30:00Z",
    "updated_at": "2023-12-10T10:30:00Z"
  }
}
```

---

### 4. Verify OTP (Vendor Login)
**Endpoint:** `/api/auth/verify-otp/`  
**Method:** `POST`  
**Authentication:** Not Required  
**Description:** Verify OTP and get authentication token for vendor

**Request Body:**
```json
{
  "email": "vendor@example.com",
  "otp": "123456",
  "user_type": "vendor"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "user_exists": true,
  "token": "a1b2c3d4e5f6g7h8i9j0...",
  "user": {
    "user_id": 2,
    "email": "vendor@example.com",
    "country_code": "+91",
    "phone_number": "9876543211",
    "full_phone": "+919876543211",
    "user_type": "vendor",
    "is_verified": true,
    "is_active": true,
    "is_staff": false,
    "created_at": "2023-12-10T10:30:00Z",
    "updated_at": "2023-12-10T10:30:00Z"
  },
  "profile": {
    "first_name": "Shop",
    "last_name": "Owner",
    "full_name": "Shop Owner",
    "pincode": "560001",
    "address": "456 Business St",
    "created_at": "2023-12-10T10:30:00Z",
    "updated_at": "2023-12-10T10:30:00Z"
  }
}
```

---

### 5. Get User Profile
**Endpoint:** `/api/auth/profile/`  
**Method:** `GET`  
**Authentication:** Required (Token)  
**Headers:**
```
Authorization: Token your_token_here
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "country_code": "+91",
  "phone_number": "9876543210",
  "full_phone": "+919876543210",
  "full_name": "John Doe",
  "user_type": "customer",
  "is_verified": true,
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "pincode": "560001",
    "address": "123 Main St"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0..."
}
```

---

### 6. Create User Profile
**Endpoint:** `/api/auth/profile/`  
**Method:** `POST`  
**Authentication:** Required (Token)  
**Description:** Create profile for authenticated user (vendor or customer)

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "pincode": "560001",
  "address": "123 Main St"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Profile created successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "user_type": "customer",
    "full_name": "John Doe",
    ...
  }
}
```

---

### 7. Update User Profile (PUT/PATCH)
Same as previous documentation with added `user_type` field in responses.

---

## Vendor APIs

### 8. List Vendor's Own Services
**Endpoint:** `/api/laundry/vendor/services/`  
**Method:** `GET`  
**Authentication:** Required (Token - Vendor only)  
**Description:** List all laundry services owned by the authenticated vendor

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "vendor": 2,
    "shop_name": "Clean N Fresh Laundry",
    "description": "Professional laundry service",
    "phone_number": "+919876543210",
    "email": "info@cleannfresh.com",
    "website": "https://cleannfresh.com",
    "locationUrl": "https://maps.google.com/?q=28.7041,77.1025",
    "address": "123 Main Street",
    "district": "Delhi",
    "state": "Delhi",
    "country": "India",
    "zipcode": "110001",
    "latitude": "28.704100",
    "longitude": "77.102500",
    "pickup_start_time": "08:00:00",
    "pickup_end_time": "20:00:00",
    "delivery_start_time": "10:00:00",
    "delivery_end_time": "22:00:00",
    "rating": "4.50",
    "total_reviews": 25,
    "is_active": true,
    "created_at": "2023-12-10T10:30:00Z",
    "updated_at": "2023-12-10T10:30:00Z",
    "service_offerings": [...],
    "operating_hours": [...],
    "reviews": [...]
  }
]
```

---

## Laundry Service APIs

### 9. List All Laundry Services (Public)
**Endpoint:** `/api/laundry/services/`  
**Method:** `GET`  
**Authentication:** Not Required  
**Description:** Get list of all active laundry services (public view)

**Query Parameters:**
- `search`: Search by shop_name, district, state, or zipcode
- `ordering`: Order by rating, shop_name, or created_at

**Response (200 OK):** Same structure as vendor services list

---

### 10. Create Laundry Service (Vendor)
**Endpoint:** `/api/laundry/services/`  
**Method:** `POST`  
**Authentication:** Required (Token - Vendor only)  
**Description:** Create a new laundry service (automatically linked to vendor)

**Request Body:**
```json
{
  "shop_name": "Clean N Fresh Laundry",
  "description": "Professional laundry service",
  "phone_number": "+919876543210",
  "email": "info@cleannfresh.com",
  "website": "https://cleannfresh.com",
  "locationUrl": "https://maps.google.com/?q=28.7041,77.1025",
  "address": "123 Main Street",
  "district": "Delhi",
  "state": "Delhi",
  "country": "India",
  "zipcode": "110001",
  "latitude": "28.704100",
  "longitude": "77.102500",
  "pickup_start_time": "08:00:00",
  "pickup_end_time": "20:00:00",
  "delivery_start_time": "10:00:00",
  "delivery_end_time": "22:00:00",
  "service_offerings": [
    {
      "service_type": 1,
      "price": "50.00",
      "unit": "per item",
      "estimated_time": "2 days"
    }
  ],
  "operating_hours": [
    {
      "day_of_week": 0,
      "opening_time": "08:00:00",
      "closing_time": "20:00:00",
      "is_closed": false
    }
  ]
}
```

**Note:** `vendor` field is automatically set to the authenticated user and should NOT be included in the request.

**Response (201 Created):**
```json
{
  "id": 1,
  "vendor": 2,
  "shop_name": "Clean N Fresh Laundry",
  ...
}
```

---

### 11. Get Laundry Service Details
**Endpoint:** `/api/laundry/services/{id}/`  
**Method:** `GET`  
**Authentication:** Not Required  
**Description:** Get details of a specific laundry service (public view)

---

### 12. Update Laundry Service
**Endpoint:** `/api/laundry/services/{id}/`  
**Method:** `PUT` or `PATCH`  
**Authentication:** Required (Token - Service Owner/Vendor only)  
**Description:** Update laundry service (only the vendor who owns it)

**Request Body:** Same as create (without vendor field)

**Note:** Only the vendor who created the service can update it.

---

### 13. Delete Laundry Service
**Endpoint:** `/api/laundry/services/{id}/`  
**Method:** `DELETE`  
**Authentication:** Required (Token - Service Owner/Vendor only)  
**Description:** Delete a laundry service (only the vendor who owns it)

---

### 14. Search Laundry Services
**Endpoint:** `/api/laundry/services/search/`  
**Method:** `GET`  
**Authentication:** Not Required  
**Description:** Search laundry services by various criteria

**Query Parameters:**
- `q`: General search query (searches in shop_name, description, and address)
- `district`: Filter by district
- `state`: Filter by state
- `zipcode`: Filter by zipcode
- `city`: Filter by city (searches in district and address)

**Example:** `/api/laundry/services/search/?q=laundry&city=delhi&state=delhi`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "vendor": 2,
    "shop_name": "Clean N Fresh Laundry",
    ...
  }
]
```

---

### 15. Find Nearby Laundry Services
**Endpoint:** `/api/laundry/services/nearby/`  
**Method:** `GET`  
**Authentication:** Not Required  
**Description:** Find laundry services near a location

**Query Parameters:**
- `lat`: Latitude (required)
- `lng`: Longitude (required)
- `radius`: Radius in kilometers (default: 10)

**Example:** `/api/laundry/services/nearby/?lat=28.7041&lng=77.1025&radius=5`

---

## Address Search API

### 16. Search Addresses
**Endpoint:** `/api/laundry/address-search/`  
**Method:** `GET`  
**Authentication:** Not Required  
**Description:** Search for addresses, cities, states, and districts

**Query Parameters:**
- `q`: Search query (minimum 2 characters, required)
- `type`: Type of search - `all`, `district`, `state`, `city`, or `address` (default: `all`)

**Example 1 - Search All:**
`/api/laundry/address-search/?q=delhi`

**Response (200 OK):**
```json
{
  "status": "success",
  "query": "delhi",
  "results": {
    "districts": ["Delhi", "New Delhi", "South Delhi"],
    "states": ["Delhi"],
    "cities": ["Delhi", "New Delhi"],
    "addresses": [
      {
        "address": "123 Main Street, Connaught Place",
        "district": "New Delhi",
        "state": "Delhi",
        "zipcode": "110001"
      },
      {
        "address": "456 Park Road, Karol Bagh",
        "district": "Central Delhi",
        "state": "Delhi",
        "zipcode": "110005"
      }
    ]
  }
}
```

**Example 2 - Search Districts Only:**
`/api/laundry/address-search/?q=ban&type=district`

**Response (200 OK):**
```json
{
  "status": "success",
  "query": "ban",
  "results": {
    "districts": ["Bangalore Urban", "Bangalore Rural"],
    "states": [],
    "cities": [],
    "addresses": []
  }
}
```

**Example 3 - Search States Only:**
`/api/laundry/address-search/?q=kar&type=state`

**Response (200 OK):**
```json
{
  "status": "success",
  "query": "kar",
  "results": {
    "districts": [],
    "states": ["Karnataka", "Kerala"],
    "cities": [],
    "addresses": []
  }
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Query must be at least 2 characters"
}
```

**Note:** Each result category is limited to 10 results maximum.

---

## Service Type APIs

### 17. List All Service Types
**Endpoint:** `/api/laundry/service-types/`  
**Method:** `GET`  
**Authentication:** Not Required (Read), Vendor Required (Create)  

---

### 18. Create Service Type
**Endpoint:** `/api/laundry/service-types/`  
**Method:** `POST`  
**Authentication:** Required (Token - Vendor only)  

---

### 19-20. Service Type Detail Operations
**Endpoint:** `/api/laundry/service-types/{id}/`  
**Methods:** `GET`, `PUT`, `PATCH`, `DELETE`  
**Authentication:** Not Required (GET), Vendor Required (PUT/PATCH/DELETE)  

---

## Service Offering APIs

### 21. List Service Offerings
**Endpoint:** `/api/laundry/service-offerings/`  
**Method:** `GET`  
**Authentication:** Not Required (Read), Vendor Required (Create)  
**Description:** Vendors see only their own service offerings; public sees all

**Query Parameters:**
- `search`: Search by service_type name or laundry_service shop_name
- `ordering`: Order by price, service_type__name, or laundry_service__shop_name

---

### 22. Create Service Offering
**Endpoint:** `/api/laundry/service-offerings/`  
**Method:** `POST`  
**Authentication:** Required (Token - Vendor only)  
**Description:** Create offering for vendor's own services only

---

### 23-26. Service Offering Detail Operations
**Endpoint:** `/api/laundry/service-offerings/{id}/`  
**Methods:** `GET`, `PUT`, `PATCH`, `DELETE`  
**Authentication:** Not Required (GET), Vendor Required (PUT/PATCH/DELETE - own offerings only)  

---

## Operating Hours APIs

### 27. List Operating Hours
**Endpoint:** `/api/laundry/operating-hours/`  
**Method:** `GET`  
**Authentication:** Not Required (Read), Vendor Required (Create)  
**Description:** Vendors see only their own service hours; public sees all

---

### 28. Create Operating Hour
**Endpoint:** `/api/laundry/operating-hours/`  
**Method:** `POST`  
**Authentication:** Required (Token - Vendor only)  

---

### 29-32. Operating Hour Detail Operations
**Endpoint:** `/api/laundry/operating-hours/{id}/`  
**Methods:** `GET`, `PUT`, `PATCH`, `DELETE`  
**Authentication:** Not Required (GET), Vendor Required (PUT/PATCH/DELETE - own hours only)  

---

## Review APIs

### 33-40. Review Operations
All review endpoints remain the same as in the original documentation.
- Customers can create, update, and delete their own reviews
- Public can view all reviews

---

## Booking APIs

### 41-48. Booking Operations
All booking endpoints remain the same as in the original documentation.
- Customers can manage their own bookings
- Shop owners can view and update status of bookings for their services

---

## Permission Summary

### Public Access (No Authentication Required)
- **GET** all list endpoints (services, service types, offerings, hours, reviews)
- **GET** specific item details
- Search and nearby services
- Address search

### Customer Access (Authentication Required - `user_type: customer`)
- Create/update/delete own profile
- Create/update/delete own reviews
- Create/update/delete own bookings
- View own booking history

### Vendor Access (Authentication Required - `user_type: vendor`)
- All customer permissions
- Create laundry services (auto-linked to vendor)
- Update/delete own laundry services
- View own services via `/vendor/services/`
- Create/update/delete service types
- Create/update/delete service offerings (for own services)
- Create/update/delete operating hours (for own services)
- Update booking status (for bookings at their services)

---

## Key Changes from Previous Version

### 1. **Vendor System**
- Added `user_type` field to User model (`customer` or `vendor`)
- Vendors register using the same OTP flow with `user_type: "vendor"`
- Vendors automatically own all services they create

### 2. **Permission Changes**
- Replaced `IsSuperAdmin` with `IsVendor` permission
- Added `IsVendorOwner` permission for service-specific operations
- Vendors can only modify their own services, offerings, and hours

### 3. **New Endpoints**
- **POST** `/api/auth/send-otp/` - Now accepts `user_type` parameter
- **POST** `/api/auth/verify-otp/` - Now accepts `user_type` parameter
- **GET** `/api/laundry/vendor/services/` - List vendor's own services
- **GET** `/api/laundry/address-search/` - Search addresses, cities, states

### 4. **Enhanced Search**
- Service search now includes address field
- Added `city` parameter to service search
- New dedicated address search API with type filtering

### 5. **Model Changes**
- LaundryService now has `vendor` foreign key field
- User model has `user_type` field with choices

---

## Migration Guide

### For Existing Data

After updating the code, run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

**Important:** Existing LaundryService records will need a vendor assigned. You can:
1. Create a default vendor user
2. Update existing services to link to this vendor
3. Or handle this in the migration file

---

## Error Responses

All endpoints may return:

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden (Vendor-specific)
```json
{
  "detail": "You do not have permission to perform this action."
}
```
*This occurs when:*
- Non-vendor tries to create/update services
- Vendor tries to modify another vendor's service

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Summary Table

| # | Endpoint | Method | Auth Required | User Type | Description |
|---|----------|--------|---------------|-----------|-------------|
| 1 | `/api/auth/send-otp/` | POST | No | Any | Send OTP (customer/vendor) |
| 2 | `/api/auth/verify-otp/` | POST | No | Any | Verify OTP (customer/vendor) |
| 3 | `/api/auth/profile/` | GET | Yes | Any | Get user profile |
| 4 | `/api/auth/profile/` | POST | Yes | Any | Create user profile |
| 5 | `/api/auth/profile/` | PUT/PATCH | Yes | Any | Update user profile |
| 6 | `/api/laundry/vendor/services/` | GET | Yes | Vendor | List vendor's services |
| 7 | `/api/laundry/services/` | GET | No | Any | List all services |
| 8 | `/api/laundry/services/` | POST | Yes | Vendor | Create service |
| 9 | `/api/laundry/services/{id}/` | GET | No | Any | Get service details |
| 10 | `/api/laundry/services/{id}/` | PUT/PATCH | Yes | Vendor (Owner) | Update service |
| 11 | `/api/laundry/services/{id}/` | DELETE | Yes | Vendor (Owner) | Delete service |
| 12 | `/api/laundry/services/search/` | GET | No | Any | Search services |
| 13 | `/api/laundry/services/nearby/` | GET | No | Any | Find nearby services |
| 14 | `/api/laundry/address-search/` | GET | No | Any | Search addresses |
| 15-20 | Service Type endpoints | Various | Vendor | Vendor | CRUD service types |
| 21-26 | Service Offering endpoints | Various | Vendor | Vendor | CRUD offerings (own) |
| 27-32 | Operating Hours endpoints | Various | Vendor | Vendor | CRUD hours (own) |
| 33-40 | Review endpoints | Various | Customer | Customer | CRUD reviews |
| 41-48 | Booking endpoints | Various | Customer/Vendor | Both | CRUD bookings |

**Total Endpoints: 50+**

---

**Last Updated:** December 10, 2025  
**Version:** 2.0 (Vendor Edition)
