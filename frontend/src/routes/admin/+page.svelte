<svelte:options runes={true} />

<script lang="ts">
	import { adminUser } from '$lib/admin.svelte';
	import { updateLanguages } from '$lib/i18n';
	import Languages from '$lib/components/Admin/Languages.svelte';
	import MilestoneGroups from '$lib/components/Admin/MilestoneGroups.svelte';
	import Questions from '$lib/components/Admin/UserQuestions.svelte';
	import Login from '$lib/components/Admin/Login.svelte';
	import { _ } from 'svelte-i18n';
	import { onMount } from 'svelte';
	import { Tabs, TabItem } from 'flowbite-svelte';
	import { LanguageOutline, BadgeCheckOutline, ClipboardListOutline } from 'flowbite-svelte-icons';

	onMount(async () => {
		updateLanguages();
		adminUser.refresh();
	});
</script>

{#if !adminUser.value || !adminUser.value.is_superuser}
	<div class="flex w-full flex-col items-center justify-center">
		<Login />
	</div>
{:else}
	<Tabs tabStyle="underline">
		<TabItem open>
			<div slot="title" class="flex items-center gap-2">
				<BadgeCheckOutline size="md" />
				{$_('admin.milestones')}
			</div>
			<MilestoneGroups />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<ClipboardListOutline size="md" />
				{$_('admin.user-questions')}
			</div>
			<Questions />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<LanguageOutline size="md" />
				{$_('admin.languages')}
			</div>
			<Languages />
		</TabItem>
	</Tabs>
{/if}
