export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left — brand panel */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-sidebar text-sidebar-foreground">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
            ॐ
          </div>
          <span className="font-semibold text-lg tracking-tight">Dhanvantari</span>
        </div>

        <div className="space-y-6">
          <blockquote className="text-2xl font-light leading-relaxed text-sidebar-foreground/90">
            "The physician who knows the science of life, who has acquired skill in treatment, who possesses purity of mind — he is the best physician."
          </blockquote>
          <p className="text-sm text-sidebar-foreground/60">— Charaka Samhita</p>
        </div>

        <div className="space-y-2 text-sm text-sidebar-foreground/50">
          <p>Rooted in tradition. Powered by intelligence.</p>
        </div>
      </div>

      {/* Right — form */}
      <div className="flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-xs">
              ॐ
            </div>
            <span className="font-semibold text-base">Dhanvantari</span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
