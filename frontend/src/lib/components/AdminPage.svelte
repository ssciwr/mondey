<svelte:options runes={true} />

<script lang="ts">
	import { milestoneAgeGroups } from '$lib/admin.svelte';
	import Languages from '$lib/components/Admin/Languages.svelte';
	import MilestoneAgeGroups from '$lib/components/Admin/MilestoneAgeGroups.svelte';
	import MilestoneGroups from '$lib/components/Admin/MilestoneGroups.svelte';
	import Translations from '$lib/components/Admin/Translations.svelte';
	import Questions from '$lib/components/Admin/UserQuestions.svelte';
	import { TabItem, Tabs } from 'flowbite-svelte';
	import {
		BadgeCheckOutline,
		CalendarMonthOutline,
		ClipboardListOutline,
		LanguageOutline
	} from 'flowbite-svelte-icons';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	onMount(async () => {
		await milestoneAgeGroups.refresh();
	});
</script>

<Tabs tabStyle="pill">
	{#if milestoneAgeGroups.value}
		{#each milestoneAgeGroups.value as milestoneAgeGroup (milestoneAgeGroup.id)}
			<TabItem open={milestoneAgeGroup.id === milestoneAgeGroups.value[0].id}>
				<div slot="title" class="flex items-center gap-2">
					<BadgeCheckOutline size="md" />
					{`${$_('admin.milestones')} (${milestoneAgeGroup.months_min}m-${milestoneAgeGroup.months_max}m)`}
				</div>
				<MilestoneGroups milestone_age_group_id={milestoneAgeGroup.id} />
			</TabItem>
		{/each}
	{/if}
	<TabItem open={true}>
		<div slot="title" class="flex items-center gap-2">
			<ClipboardListOutline size="md" />
			{$_('admin.user-questions')}
		</div>
		<Questions />
	</TabItem>
	<TabItem>
		<div slot="title" class="flex items-center gap-2">
			<CalendarMonthOutline size="md" />
			{$_('admin.milestone-age-groups')}
		</div>
		<MilestoneAgeGroups />
	</TabItem>
	<TabItem>
		<div slot="title" class="flex items-center gap-2">
			<LanguageOutline size="md" />
			{$_('admin.translations')}
		</div>
		<Translations />
	</TabItem>
	<TabItem>
		<div slot="title" class="flex items-center gap-2">
			<LanguageOutline size="md" />
			{$_('admin.languages')}
		</div>
		<Languages />
	</TabItem>
</Tabs>
