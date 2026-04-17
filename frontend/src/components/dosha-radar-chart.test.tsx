import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import DoshaRadarChart from "./dosha-radar-chart";

// Recharts uses ResizeObserver internally; provide a minimal mock for jsdom.
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
vi.stubGlobal("ResizeObserver", ResizeObserverMock);

describe("DoshaRadarChart", () => {
  it("renders nothing when both prakriti and vikriti are absent", () => {
    const { container } = render(<DoshaRadarChart />);
    expect(container.innerHTML).toBe("");
  });

  it("renders nothing when both props are null", () => {
    const { container } = render(
      <DoshaRadarChart prakriti={null} vikriti={null} />
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders a chart container when prakriti is provided", () => {
    const prakriti = { vata: 8, pitta: 5, kapha: 3 };
    const { container } = render(<DoshaRadarChart prakriti={prakriti} />);
    // The component wraps the chart in a div with className containing "flex"
    const wrapper = container.querySelector("div.flex");
    expect(wrapper).not.toBeNull();
  });

  it("renders a chart container when vikriti is provided", () => {
    const vikriti = { vata: 4, pitta: 7, kapha: 2 };
    const { container } = render(<DoshaRadarChart vikriti={vikriti} />);
    const wrapper = container.querySelector("div.flex");
    expect(wrapper).not.toBeNull();
  });

  it("renders with both prakriti and vikriti", () => {
    const prakriti = { vata: 8, pitta: 5, kapha: 3 };
    const vikriti = { vata: 4, pitta: 7, kapha: 2 };
    const { container } = render(
      <DoshaRadarChart prakriti={prakriti} vikriti={vikriti} />
    );
    const wrapper = container.querySelector("div.flex");
    expect(wrapper).not.toBeNull();
  });

  it("renders chart wrapper with content when data is provided", () => {
    const prakriti = { vata: 8, pitta: 5, kapha: 3 };
    const { container } = render(<DoshaRadarChart prakriti={prakriti} />);
    // The outer flex div should contain child elements from Recharts
    const wrapper = container.querySelector("div.flex");
    expect(wrapper).not.toBeNull();
    expect(wrapper!.children.length).toBeGreaterThan(0);
  });
});
