import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "../App";
import { validateForm } from "../validation";

function renderApp() {
  return render(<App />);
}

// Unit tests for the pure validation function
describe("validateForm", () => {
  it("returns errors for all empty fields", () => {
    const errors = validateForm({ name: "", email: "", message: "" });
    expect(errors.name).toBe("Name is required");
    expect(errors.email).toBe("Email is required");
    expect(errors.message).toBe("Message is required");
  });

  it("returns an error for an invalid email format", () => {
    const errors = validateForm({
      name: "Alice",
      email: "not-an-email",
      message: "Hello",
    });
    expect(errors.email).toBe("Invalid email address");
  });

  it("returns no errors when all fields are valid", () => {
    const errors = validateForm({
      name: "Alice",
      email: "alice@example.com",
      message: "Hello",
    });
    expect(Object.keys(errors)).toHaveLength(0);
  });
});

// Integration tests for the Contact form UI
describe("Contact form UI", () => {
  it("shows validation errors when the empty form is submitted", () => {
    renderApp();
    fireEvent.click(screen.getByRole("link", { name: /contact/i }));
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    expect(screen.getByText("Name is required")).toBeInTheDocument();
    expect(screen.getByText("Email is required")).toBeInTheDocument();
    expect(screen.getByText("Message is required")).toBeInTheDocument();
  });

  it("clears the field error when the user starts typing", () => {
    renderApp();
    fireEvent.click(screen.getByRole("link", { name: /contact/i }));

    fireEvent.click(screen.getByRole("button", { name: /submit/i }));
    expect(screen.getByText("Name is required")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Name"), {
      target: { name: "name", value: "B" },
    });
    expect(screen.queryByText("Name is required")).not.toBeInTheDocument();
  });

  it("renders nav links for all three routes", () => {
    renderApp();
    expect(screen.getByRole("link", { name: /home/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /about/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /contact/i })).toBeInTheDocument();
  });
});
