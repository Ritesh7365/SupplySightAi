export default function HomePage() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_20%_20%,hsl(174_45%_88%/_0.9),transparent_50%),radial-gradient(ellipse_at_80%_10%,hsl(28_70%_90%/_0.55),transparent_45%),linear-gradient(165deg,hsl(210_28%_97%)_0%,hsl(210_22%_92%)_100%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.35] [background-image:linear-gradient(hsl(210_20%_70%/_0.15)_1px,transparent_1px),linear-gradient(90deg,hsl(210_20%_70%/_0.15)_1px,transparent_1px)] [background-size:48px_48px] animate-fade-in"
      />

      <div className="relative z-10 mx-auto flex max-w-3xl flex-col items-center text-center">
        <h1 className="font-display text-5xl leading-none tracking-tight text-foreground sm:text-7xl animate-fade-up">
          SupplySight AI
        </h1>
        <p className="mt-6 max-w-xl text-base text-muted-foreground sm:text-lg animate-fade-up [animation-delay:120ms]">
          Enterprise Supply Chain Analytics Platform
        </p>
      </div>
    </main>
  );
}
