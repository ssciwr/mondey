<script>
import { BottomNavItem, Tooltip } from "flowbite-svelte";

export let description;
export let href;
export let Icon;
export let tooltip;
export let componentProps = {};
</script>

<BottomNavItem {href} btnName={description}>
	<svelte:component this={Icon} {...componentProps} />
	<Tooltip arrow={false}>{tooltip}</Tooltip>
</BottomNavItem>
