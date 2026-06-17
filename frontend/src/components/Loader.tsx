export function Loader() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true" aria-label="Loading squad">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="h-20 rounded-xl border border-white/10 bg-slate-900/70" />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="h-[26rem] rounded-2xl border border-white/10 bg-slate-900/70" />
          <div className="h-32 rounded-2xl border border-white/10 bg-slate-900/70" />
        </div>
        <div className="h-96 rounded-2xl border border-white/10 bg-slate-900/70" />
      </div>
    </div>
  )
}
