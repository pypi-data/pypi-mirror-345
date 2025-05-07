#!/usr/bin/env python3

import argparse
import os
from contextlib import nullcontext

from grazie.api.client.chat.prompt import ChatPrompt
from grazie.api.client.completion.prompt import CompletionPrompt
from grazie.api.client.endpoints import GrazieApiGatewayUrls
from grazie.api.client.gateway import AuthType, GrazieAgent, GrazieApiGatewayClient
from grazie.api.client.profiles import LLMProfile, Profile


def get_client(args: argparse.Namespace) -> GrazieApiGatewayClient:
    return GrazieApiGatewayClient(
        grazie_agent=GrazieAgent(name="grazie-api-gateway-client", version="dev"),
        url=args.gateway,
        auth_type=AuthType.USER,
        grazie_jwt_token=args.token,
    )


def completion(args: argparse.Namespace) -> None:
    client = get_client(args)

    response = client.complete(
        prompt=CompletionPrompt(args.prompt),
        profile=Profile.get_by_name(args.profile),
    )

    print(response.completion)


def chat(args: argparse.Namespace) -> None:
    client = get_client(args)

    response = client.chat(
        chat=ChatPrompt().add_system(args.system).add_user(args.prompt),
        profile=Profile.get_by_name(args.profile),
    )

    print(response.content)


def main() -> None:
    profiles = sorted(
        [
            value.name
            for attr in dir(Profile)
            for value in (getattr(Profile, attr),)
            if isinstance(value, LLMProfile)
        ]
    )

    parser = argparse.ArgumentParser(description="Grazie API Gateway Client")
    parser.add_argument("-g", "--gateway", type=str, default=GrazieApiGatewayUrls.STAGING)
    parser.add_argument("-p", "--profile", choices=profiles, default=Profile.OPENAI_CHAT_GPT.name)
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        default=os.environ.get("GRAZIE_JWT_TOKEN", None),
        help=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers()

    with nullcontext(subparsers.add_parser("completion")) as subparser:
        subparser.add_argument("prompt")
        subparser.set_defaults(func=completion)

    with nullcontext(subparsers.add_parser("chat")) as subparser:
        subparser.add_argument("-s", "--system", type=str, default="You are a helpful assistant.")
        subparser.add_argument("prompt")
        subparser.set_defaults(func=chat)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
