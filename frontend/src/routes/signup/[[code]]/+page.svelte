<script lang="ts">
import { page } from "$app/state";
import UserRegistration from "$lib/components/UserRegistration.svelte";
</script>

<UserRegistration researchCode={page.params.code}/>
