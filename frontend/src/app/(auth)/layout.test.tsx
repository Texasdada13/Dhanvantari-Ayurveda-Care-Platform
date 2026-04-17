import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import AuthLayout from "./layout";

describe("AuthLayout", () => {
  it("renders children inside the layout", () => {
    render(
      <AuthLayout>
        <div data-testid="child">Login Form</div>
      </AuthLayout>
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
    expect(screen.getByText("Login Form")).toBeInTheDocument();
  });

  it("displays the Dhanvantari brand name", () => {
    render(
      <AuthLayout>
        <span>test</span>
      </AuthLayout>
    );
    // Brand name appears in both desktop and mobile versions
    const brandElements = screen.getAllByText("Dhanvantari");
    expect(brandElements.length).toBeGreaterThanOrEqual(1);
  });

  it("shows the Charaka Samhita quote on desktop panel", () => {
    render(
      <AuthLayout>
        <span>test</span>
      </AuthLayout>
    );
    expect(screen.getByText(/Charaka Samhita/)).toBeInTheDocument();
  });

  it("renders the Om symbol in the brand logo", () => {
    render(
      <AuthLayout>
        <span>test</span>
      </AuthLayout>
    );
    const omSymbols = screen.getAllByText("\u0950");
    expect(omSymbols.length).toBeGreaterThanOrEqual(1);
  });

  it("renders the tagline text", () => {
    render(
      <AuthLayout>
        <span>test</span>
      </AuthLayout>
    );
    expect(
      screen.getByText("Rooted in tradition. Powered by intelligence.")
    ).toBeInTheDocument();
  });
});
