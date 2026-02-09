"use client";
import "./globals.css";
import { useState } from "react";

export default function Home() {
  const [result, setResult] = useState<string[]>([]);
  const [inputString, setInputString] = useState<string>("-113/-113, -113/-113");
  const [bankroll, setBankroll] = useState<string>("100");
  const [kellyFraction, setKellyFraction] = useState<string>("0.25");
  const [finalOdds, setFinalOdds] = useState<string>("324");
  const [devigMethod, setDevigMethod] = useState<string>("worst_case");
  
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleClick = async () => {
    try {
      const response = await fetch(`${API_URL}/calculate-bet?input_str=${encodeURIComponent(inputString)}&final_odds=${finalOdds}&bankroll=${bankroll}&kelly_fraction=${kellyFraction}&devig_method=${devigMethod}`);
      const data = await response.json();
      
      if (data.output) {
        const sanitizedOutput = data.output.map((line: string) => line.replace(/<[^>]*>/g, ''));
        setResult(sanitizedOutput);
      } else if (data.error) {
        const sanitizedError = data.error.replace(/<[^>]*>/g, '');
        setResult([`Error: ${sanitizedError}`]);
      } else {
        setResult(["No output received"]);
      }
    } catch (error) {
      setResult(["Error: Could not connect to API"]);
    }
  };
  
      return (
        <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
          <header>
            <h1>QK Calculator</h1>
            <p style={{ color: "#666", marginTop: "8px" }}>
              Quarter Kelly & Devig Calculator
            </p>
          </header>
          
          <div style={{ display: "flex", gap: "40px", marginTop: "20px" }}>
            <div style={{ flex: "1", minWidth: "400px" }}>
      
      <div style={{ margin: "20px 0" }}>
        <label htmlFor="odds-input" style={{ display: "block", marginBottom: "10px", fontWeight: "bold" }}>
          Enter odds (comma-separated):
        </label>
            <input
              id="odds-input"
              type="text"
              value={inputString}
              onChange={(e) => setInputString(e.target.value)}
              placeholder="-113/-113, -113/-113"
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontSize: "14px",
                color: "#000",
                backgroundColor: "#fff"
              }}
            />
      </div>

      <div style={{ margin: "20px 0" }}>
        <label htmlFor="final-odds" style={{ display: "block", marginBottom: "10px", fontWeight: "bold" }}>
          Final Odds:
        </label>
        <input
          id="final-odds"
          type="text"
          value={finalOdds}
          onChange={(e) => setFinalOdds(e.target.value)}
          placeholder="324"
          style={{
            width: "100%",
            padding: "8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "14px",
            color: "#000",
            backgroundColor: "#fff"
          }}
        />
      </div>

      <div style={{ margin: "20px 0" }}>
        <label htmlFor="bankroll" style={{ display: "block", marginBottom: "10px", fontWeight: "bold" }}>
          Bankroll ($):
        </label>
        <input
          id="bankroll"
          type="text"
          value={bankroll}
          onChange={(e) => setBankroll(e.target.value)}
          placeholder="100"
          style={{
            width: "100%",
            padding: "8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "14px",
            color: "#000",
            backgroundColor: "#fff"
          }}
        />
      </div>

      <div style={{ margin: "20px 0" }}>
        <label htmlFor="kelly-fraction" style={{ display: "block", marginBottom: "10px", fontWeight: "bold" }}>
          Kelly Fraction:
        </label>
        <input
          id="kelly-fraction"
          type="text"
          value={kellyFraction}
          onChange={(e) => setKellyFraction(e.target.value)}
          placeholder="0.25"
          style={{
            width: "100%",
            padding: "8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "14px",
            color: "#000",
            backgroundColor: "#fff"
          }}
        />
      </div>

      <div style={{ margin: "20px 0" }}>
        <label htmlFor="devig-method" style={{ display: "block", marginBottom: "10px", fontWeight: "bold" }}>
          Devig Method:
        </label>
            <select
              id="devig-method"
              value={devigMethod}
              onChange={(e) => setDevigMethod(e.target.value)}
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontSize: "14px",
                backgroundColor: "black",
                color: "white"
              }}
            >
              <option value="worst_case">Worst Case</option>
              <option value="multiplicative">Multiplicative</option>
              <option value="additive">Additive</option>
              <option value="power">Power</option>
            </select>
      </div>
      
              <button onClick={handleClick} className="runbutton" style={{ width: "100%", padding: "12px", fontSize: "16px" }}> 
                Calculate Bet
              </button>
            </div>
            
            <div style={{ flex: "1", minWidth: "400px" }}>
              <h2 style={{ marginBottom: "20px" }}>Results</h2>
              <div style={{
                backgroundColor: "#f8f9fa",
                padding: "20px",
                borderRadius: "8px",
                border: "1px solid #e9ecef",
                minHeight: "200px"
              }}>
                {result.length > 0 ? (
                  <div style={{ fontFamily: "monospace", fontSize: "14px", lineHeight: "1.6", color: "#000" }}>
                    {result.map((line, index) => (
                      <div key={index} style={{ marginBottom: "8px" }}>
                        {line}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: "#666", fontStyle: "italic" }}>
                    Click "Calculate Bet" to see results here
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
  );
}
