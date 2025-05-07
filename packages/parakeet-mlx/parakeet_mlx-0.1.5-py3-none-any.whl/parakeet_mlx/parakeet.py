from dataclasses import dataclass
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn

from parakeet_mlx import tokenizer
from parakeet_mlx.alignment import (
    AlignedResult,
    AlignedToken,
    sentences_to_result,
    tokens_to_sentences,
)
from parakeet_mlx.audio import PreprocessArgs, get_logmel, load_audio
from parakeet_mlx.conformer import Conformer, ConformerArgs
from parakeet_mlx.ctc import AuxCTCArgs, ConvASRDecoder
from parakeet_mlx.rnnt import JointArgs, JointNetwork, PredictArgs, PredictNetwork


@dataclass
class TDTDecodingArgs:
    model_type: str
    durations: list[int]
    greedy: dict | None


@dataclass
class RNNTDecodingArgs:
    greedy: dict | None


@dataclass
class ParakeetTDTArgs:
    preprocessor: PreprocessArgs
    encoder: ConformerArgs
    decoder: PredictArgs
    joint: JointArgs
    decoding: TDTDecodingArgs


@dataclass
class ParakeetRNNTArgs:
    preprocessor: PreprocessArgs
    encoder: ConformerArgs
    decoder: PredictArgs
    joint: JointArgs
    decoding: RNNTDecodingArgs


@dataclass
class ParakeetTDTCTCArgs(ParakeetTDTArgs):
    aux_ctc: AuxCTCArgs


class BaseParakeet(nn.Module):
    """Base parakeet model for interface purpose"""

    def __init__(self, preprocess_args: PreprocessArgs):
        super().__init__()

        self.preprocessor_config = preprocess_args

    def generate(self, mel: mx.array) -> list[AlignedResult]:
        """
        Generate with skip token logic for the Parakeet model, handling batches and single input. Uses greedy decoding.
        mel: [batch, sequence, mel_dim] or [sequence, mel_dim]
        """
        raise NotImplementedError

    def transcribe(
        self, path: Path | str, *, dtype: mx.Dtype = mx.bfloat16
    ) -> AlignedResult:
        """Transcribe an audio file, path must be provided."""
        audio = load_audio(Path(path), self.preprocessor_config.sample_rate, dtype)
        mel = get_logmel(audio, self.preprocessor_config)

        return self.generate(mel)[0]


class ParakeetTDT(BaseParakeet):
    """MLX Implementation of Parakeet-TDT Model"""

    def __init__(self, args: ParakeetTDTArgs):
        super().__init__(args.preprocessor)

        assert args.decoding.model_type == "tdt", "Model must be a TDT model"

        self.encoder_config = args.encoder

        self.vocabulary = args.joint.vocabulary
        self.durations = args.decoding.durations
        self.max_symbols: int | None = (
            args.decoding.greedy.get("max_symbols", None)
            if args.decoding.greedy
            else None
        )

        self.encoder = Conformer(args.encoder)
        self.decoder = PredictNetwork(args.decoder)
        self.joint = JointNetwork(args.joint)

    def generate(self, mel: mx.array) -> list[AlignedResult]:
        """
        Generate with skip token logic for the Parakeet model, handling batches and single input. Uses greedy decoding.
        mel: [batch, sequence, mel_dim] or [sequence, mel_dim]
        """
        batch_size: int = mel.shape[0]
        if len(mel.shape) == 2:
            batch_size = 1
            mel = mx.expand_dims(mel, 0)

        batch_features, lengths = self.encoder(mel)
        mx.eval(batch_features, lengths)

        results = []
        for b in range(batch_size):
            features = batch_features[b : b + 1]
            max_length = int(lengths[b])

            last_token = len(
                self.vocabulary
            )  # In TDT, space token is always len(vocab)
            hypothesis = []

            time = 0
            new_symbols = 0
            decoder_hidden = None

            while time < max_length:
                feature = features[:, time : time + 1]

                current_token = (
                    mx.array([[last_token]], dtype=mx.int32)
                    if last_token != len(self.vocabulary)
                    else None
                )
                decoder_output, (hidden, cell) = self.decoder(
                    current_token, decoder_hidden
                )

                # cast
                decoder_output = decoder_output.astype(feature.dtype)
                proposed_decoder_hidden = (
                    hidden.astype(feature.dtype),
                    cell.astype(feature.dtype),
                )

                joint_output = self.joint(feature, decoder_output)

                pred_token = mx.argmax(
                    joint_output[0, 0, :, : len(self.vocabulary) + 1]
                )
                decision = mx.argmax(joint_output[0, 0, :, len(self.vocabulary) + 1 :])

                if pred_token != len(self.vocabulary):
                    hypothesis.append(
                        AlignedToken(
                            int(pred_token),
                            start=time
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            duration=self.durations[int(decision)]
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            text=tokenizer.decode([int(pred_token)], self.vocabulary),
                        )
                    )
                    last_token = int(pred_token)
                    decoder_hidden = proposed_decoder_hidden

                time += self.durations[int(decision)]
                new_symbols += 1

                if self.durations[int(decision)] != 0:
                    new_symbols = 0
                else:
                    if self.max_symbols is not None and self.max_symbols <= new_symbols:
                        time += 1
                        new_symbols = 0

            result = sentences_to_result(tokens_to_sentences(hypothesis))
            results.append(result)

        return results


class ParakeetRNNT(BaseParakeet):
    """MLX Implementation of Parakeet-RNNT Model"""

    def __init__(self, args: ParakeetRNNTArgs):
        super().__init__(args.preprocessor)

        self.encoder_config = args.encoder

        self.vocabulary = args.joint.vocabulary
        self.max_symbols: int | None = (
            args.decoding.greedy.get("max_symbols", None)
            if args.decoding.greedy
            else None
        )

        self.encoder = Conformer(args.encoder)
        self.decoder = PredictNetwork(args.decoder)
        self.joint = JointNetwork(args.joint)

    def generate(self, mel: mx.array) -> list[AlignedResult]:
        """
        Generate with skip token logic for the Parakeet model, handling batches and single input. Uses greedy decoding.
        mel: [batch, sequence, mel_dim] or [sequence, mel_dim]
        """
        batch_size: int = mel.shape[0]
        if len(mel.shape) == 2:
            batch_size = 1
            mel = mx.expand_dims(mel, 0)

        batch_features, lengths = self.encoder(mel)
        mx.eval(batch_features, lengths)

        results = []
        for b in range(batch_size):
            features = batch_features[b : b + 1]
            max_length = int(lengths[b])

            last_token = len(self.vocabulary)
            hypothesis = []

            time = 0
            new_symbols = 0
            decoder_hidden = None

            while time < max_length:
                feature = features[:, time : time + 1]

                current_token = (
                    mx.array([[last_token]], dtype=mx.int32)
                    if last_token != len(self.vocabulary)
                    else None
                )
                decoder_output, (hidden, cell) = self.decoder(
                    current_token, decoder_hidden
                )

                # cast
                decoder_output = decoder_output.astype(feature.dtype)
                proposed_decoder_hidden = (
                    hidden.astype(feature.dtype),
                    cell.astype(feature.dtype),
                )

                joint_output = self.joint(feature, decoder_output)

                pred_token = mx.argmax(joint_output)

                if pred_token != len(self.vocabulary):
                    hypothesis.append(
                        AlignedToken(
                            int(pred_token),
                            start=time
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            duration=1
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            text=tokenizer.decode([int(pred_token)], self.vocabulary),
                        )
                    )
                    last_token = int(pred_token)
                    decoder_hidden = proposed_decoder_hidden

                    new_symbols += 1
                    if self.max_symbols is not None and self.max_symbols <= new_symbols:
                        time += 1
                        new_symbols = 0
                else:
                    time += 1
                    new_symbols = 0

            result = sentences_to_result(tokens_to_sentences(hypothesis))
            results.append(result)

        return results


class ParakeetTDTCTC(ParakeetTDT):
    """MLX Implementation of Parakeet-TDT-CTC Model

    Has ConvASRDecoder decoder in `.ctc_decoder` but `.generate` uses TDT decoder all the times (Please open an issue if you need CTC decoder use-case!)"""

    def __init__(self, args: ParakeetTDTCTCArgs):
        super().__init__(args)

        self.ctc_decoder = ConvASRDecoder(args.aux_ctc.decoder)
