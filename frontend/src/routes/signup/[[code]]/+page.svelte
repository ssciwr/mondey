<script lang="ts">
import { page } from "$app/stores";
import UserRegistration from "$lib/components/UserRegistration.svelte";
</script>

<UserRegistration researchCode={$page.params.code}/>
