<script lang="ts">
import babyFlower from "$lib/assets/babyFlower.jpg";
import {authCookieLogin, registerRegister} from "$lib/client/services.gen";
import { i18n } from "$lib/i18n.svelte";
import {Button, Card} from "flowbite-svelte";
import type {AuthCookieLoginData, RegisterRegisterData, UserCreate, ValidationError} from "$lib/client/index.js";
import {goto} from "$app/navigation";
import {refresh} from "$lib/utils/Login";

let showAlert = $state(false);
let alertMessage = $state(
        i18n.tr.childData.alertMessageError as string | ValidationError[] | undefined,
);
let success = $state(false)

let testAccountData: UserCreate = {
  email: ((Math.random()+0.1)*100000000).toString() + "tester@testaccount.com",
  password: ((Math.random()+0.1)*100000000).toString(), // random 8 digit or more password
  is_active: true,
  research_group_id: 0
}
let registerRequestTestAccountData: RegisterRegisterData = {
  body: testAccountData
};

const registerTestUser = async () => {
  const result = await registerRegister(registerRequestTestAccountData);

  if (result.error) {
    console.log("error: ", result.response.status, result.error.detail);
    alertMessage = `${i18n.tr.registration.alertMessageError}: ${result.error.detail}`;
    showAlert = true;
  } else {
    success = true;
    console.log('Successful response:', result.response)
    const loginData: AuthCookieLoginData = {
      body: {
        username: testAccountData.email,
        password: testAccountData.password,
      },
    };

    const authReturn = await authCookieLogin(loginData);

    if (authReturn.error) {
      showAlert = true;
      alertMessage = i18n.tr.login.badCredentials + authReturn.error.detail;
      console.log("error during login ", authReturn.error.detail);
    } else {
      const status: string = await refresh();
      if (status !== "success") {
        alertMessage = `${i18n.tr.login.badCredentials}`;
      }
      await goto('/userLand/userLandingpage')
    }
  }
}

</script>

  <div class="flex mt-6 justify-center min-w-full">
    <Card horizontal class="max-w-4xl shadow-none border-none flex items-start space-x-6">
      <img src={babyFlower} alt="{i18n.tr.frontpageAbout.alt}" class="rounded-lg md:w-1/3 max-md:aspect-[16/8] max-md:object-cover">
      <div class="flex items-start flex-col">
      <h5 class="mb-8 mt-5 text-2xl font-bold tracking-tight text-gray-700 dark:text-white">{i18n.tr.frontpageAbout.heading}</h5>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{i18n.tr.frontpageAbout.summary1}</p>
      <p class="mb-3 font-normal max-w-prose text-gray-700 dark:text-gray-400">{i18n.tr.frontpageAbout.summary2}</p>

        <Button class="btn-primary" on:click={() => registerTestUser()}>Try Demo</Button>
      </div>
    </Card>
  </div>
