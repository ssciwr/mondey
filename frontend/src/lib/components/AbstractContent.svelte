<script>
import { BottomNav } from "flowbite-svelte";

// logo
import BottomNavElement from "$lib/components/Navigation/BottomNavElement.svelte";
import {
	CaretLeftSolid,
	CaretRightSolid,
	LightbulbSolid,
} from "flowbite-svelte-icons";

// variables for showing or hiding elements
export let showBottomNavbar = true;

// variables for communication upon hitting the page
// FIXME: these are placeholders and must later be changed using contexts or other better mechanisms for inter component comunication
export let lastpage = null;
export let nextpage = null;
export let infopage = null;
</script>

<!-- Top element: basic navigation-->

<!--Page content goes here-->
<div
	class="container mx-auto max-w-6xl flex-1 items-center justify-center overflow-x-auto overflow-y-auto p-4 pb-20"
>
	<slot></slot>
</div>

{#if showBottomNavbar}
	<BottomNav
		class="fixed bottom-0 left-0 right-0 justify-center border-t border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800"
		classInner="grid-cols-3"
	>
		{#if lastpage}
			<BottomNavElement
				href={lastpage}
				description={'Zurück'}
				Icon={CaretLeftSolid}
				tooltip={'Zur letzten Seite'}
			/>
		{/if}

		{#if infopage}
			<BottomNavElement
				href={infopage}
				description={'Hilfe'}
				Icon={LightbulbSolid}
				tooltip={'Zusätzliche Informationen'}
			/>
		{/if}
		{#if nextpage}
			<BottomNavElement
				href={nextpage}
				description={'Weiter'}
				Icon={CaretRightSolid}
				tooltip={'Zur nächsten Seite'}
			/>
		{/if}
	</BottomNav>
{/if}
