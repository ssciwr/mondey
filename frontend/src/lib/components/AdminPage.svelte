<svelte:options runes={true} />

<script lang="ts">
import { adminUser } from "$lib/admin.svelte";
import Languages from "$lib/components/Admin/Languages.svelte";
import MilestoneGroups from "$lib/components/Admin/MilestoneGroups.svelte";
import Questions from "$lib/components/Admin/Questions.svelte";
import Translations from "$lib/components/Admin/Translations.svelte";
import { TabItem, Tabs } from "flowbite-svelte";
import {
	BadgeCheckOutline,
	ClipboardListOutline,
	LanguageOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";

onMount(async () => {
	adminUser.refresh();
});
</script>

<Tabs tabStyle="underline" class="w-full">
		<TabItem open>
			<div slot="title" class="flex items-center gap-2">
				<BadgeCheckOutline size="md" />
				{$_("admin.milestones")}
			</div>
			<MilestoneGroups />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<ClipboardListOutline size="md" />
				{$_("admin.user-questions")}
			</div>
			<Questions kind={"user"} />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<ClipboardListOutline size="md" />
				{$_("admin.child-questions")}
			</div>
			<Questions kind={"child"} />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<LanguageOutline size="md" />
				{$_("admin.translations")}
			</div>
			<Translations />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<LanguageOutline size="md" />
				{$_("admin.languages")}
			</div>
			<Languages />
		</TabItem>
</Tabs>
