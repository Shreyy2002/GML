export default function Skeleton({ className = 'h-6 w-full' }: { className?: string }) {
  return <div className={`${className} animate-pulse rounded-md bg-slate-200`} />;
}
