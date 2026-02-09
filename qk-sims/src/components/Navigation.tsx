"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav style={{
      backgroundColor: "#1a1a1a",
      padding: "12px 20px",
      borderBottom: "1px solid #333",
      display: "flex",
      gap: "20px",
      alignItems: "center"
    }}>
      <div style={{
        fontSize: "18px",
        fontWeight: "bold",
        color: "#fff",
        marginRight: "20px"
      }}>
        Betting Calculator
      </div>
      
      <Link 
        href="/" 
        style={{
          padding: "8px 16px",
          borderRadius: "4px",
          textDecoration: "none",
          color: pathname === "/" ? "#fff" : "#ccc",
          backgroundColor: pathname === "/" ? "#007bff" : "transparent",
          transition: "all 0.2s ease",
          fontWeight: pathname === "/" ? "bold" : "normal"
        }}
      >
        QK Calculator
      </Link>
      
      <Link 
        href="/scenario-simulator" 
        style={{
          padding: "8px 16px",
          borderRadius: "4px",
          textDecoration: "none",
          color: pathname === "/scenario-simulator" ? "#fff" : "#ccc",
          backgroundColor: pathname === "/scenario-simulator" ? "#007bff" : "transparent",
          transition: "all 0.2s ease",
          fontWeight: pathname === "/scenario-simulator" ? "bold" : "normal"
        }}
      >
        Scenario Simulator
      </Link>
    </nav>
  );
}
