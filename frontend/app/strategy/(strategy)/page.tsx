// import CardWrapper from '@/app/components/dashboard/cards';
// import { Card } from "@/app/components/dashboard/cards";
// import RevenueChart from "@/app/components/dashboard/revenue-chart";
// import LatestInvoices from "@/app/components/dashboard/latest-invoices";
import { lusitana } from "@/app/ui/fonts";
// import { fetchCardData } from '@/app/lib/data'; // Remove fetchLatestInvoices
// import { Suspense } from "react";
// import {
//   RevenueChartSkeleton,
//   LatestInvoicesSkeleton,
// } from "@/app/components/skeletons";

export default async function Page() {
	// Remove `const latestInvoices = await fetchLatestInvoices()`
	// const {
	// 	numberOfInvoices,
	// 	numberOfCustomers,
	// 	totalPaidInvoices,
	// 	totalPendingInvoices,
	// } = await fetchCardData();

	return (
		<main>
			<h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
				Dashboard
			</h1>
			<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
				{/*<Suspense fallback={<CardsSkeleton />}>
					<CardWrapper />
				</Suspense> */}
				<p>
					GG
				</p>
			</div>

			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<p>
				DDD
			</p>
			<div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-4 lg:grid-cols-8">
				{/* <Suspense fallback={<RevenueChartSkeleton />}>
					<RevenueChart />
				</Suspense>
				<Suspense fallback={<LatestInvoicesSkeleton />}>
					<LatestInvoices />
				</Suspense> */}
			</div>
		</main>
	);
}