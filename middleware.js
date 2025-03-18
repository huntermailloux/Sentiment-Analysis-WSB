import { NextResponse } from "next/server";

export function middleware(req) {
    const res = NextResponse.next();
    
    res.headers.set("Access-Control-Allow-Origin", "https://www.wsb-analysis.ca");
    res.headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");

    return res;
}

// Apply middleware to API routes only
export const config = {
    matcher: "/api/:path*",
};
